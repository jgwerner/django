const chakram = require('chakram')
const util = require('util')
const config = require('./config')
const tools = require('./test_utils')
const faker = require('faker')
const fs = require('fs')
const expect = chakram.expect

const namespace = config.username

before(async () => {
  // login
  const token = await tools.login(config.username, config.password)
  this.options = {
    headers: {
      Authorization: util.format('%s %s', 'Bearer', token),
    },
  }

  // seed a project for tests
  const proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))
  const shared_proj = tools.generate_project()

  const response = await chakram.post(proj_uri, shared_proj, this.options)
  expect(response).to.have.status(201)
  this.shared_proj = response.body

  const size_uri = tools.get_request_uri('servers/options/server-size/')
  const size_response = await chakram.get(size_uri, this.options)
  this.nano = size_response.body.find(s => s.name === 'Nano')

  // seed a server for tests
  this.servers_uri = tools.get_request_uri(
    util.format('%s/projects/%s/servers/', namespace, this.shared_proj.id),
  )
  const server = tools.generate_server(this.nano.id)
  const server_response = await chakram.post(this.servers_uri, server, this.options)
  expect(response).to.have.status(201)
  this.shared_server = server_response.body

  console.log('Shared Project: %s', this.shared_proj.id)
  console.log('Shared Server: %s', this.shared_server.id)
})

describe('{namespace}/projects/', () => {
  let proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))
  let object_schema = {
    type: 'object',
    properties: {
      id: {
        type: 'string',
      },
      name: {
        type: 'string',
      },
      description: {
        type: 'string',
      },
      private: {
        type: 'boolean',
      },
      last_updated: {
        type: 'string',
      },
      team: {
        type: ['null', 'string'],
      },
      owner: {
        type: 'string',
      },
      collaborators: {
        type: 'array',
        items: {
          type: 'string',
        },
      },
      copying_enabled: {
        type: 'boolean',
      },
    },
  }
  let array_schema = {
    type: 'array',
    items: object_schema,
  }

  afterEach(async () => {
    if (this.project_id) {
      const delete_uri = proj_uri + this.project_id + '/'
      const response = await chakram.delete(delete_uri, {}, this.options)
      expect(response).to.have.status(204)
      this.project_id = undefined
    }
  })

  it('POST a valid project should create the project', async () => {
    let new_proj = tools.generate_project()
    let response = await chakram.post(proj_uri, new_proj, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(new_proj)
    this.project_id = response.body.id
  })

  it('GET all projects should return a list of projects', async () => {
    let new_proj = tools.generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    this.project_id = post_response.body.id

    const get_response = await chakram.get(proj_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific project should return the project', async () => {
    let new_proj = tools.generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    this.project_id = post_response.body.id
    const uri = proj_uri + this.project_id + '/'

    const get_response = await chakram.get(uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
    expect(get_response).to.have.json('id', this.project_id)
  })

  it.skip('DELETE a project should remove the project | ISSUE #624', async () => {
    let project_uri
    let new_proj = tools.generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    project_uri = proj_uri + response.body.id + '/'

    const delete_response = await chakram.delete(project_uri, {}, this.options)
    expect(delete_response).to.have.status(204)

    const get_response = await chakram.get(project_uri, this.options)
    expect(get_response).to.have.status(404)
  })

  it('PUT a project should replace the project', async () => {
    let new_proj = tools.generate_project()
    let mod_proj = tools.generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    const uri = proj_uri + post_response.body.id + '/'

    const put_response = await chakram.put(uri, mod_proj, this.options)
    expect(put_response).to.have.status(200)

    const get_response = await chakram.get(uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.comprise.of.json(mod_proj)
  })

  it('PATCH a project should replace the project', async () => {
    let project_uri
    let new_proj = tools.generate_project()
    let mod_proj = tools.generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    project_uri = proj_uri + post_response.body.id + '/'

    const patch_response = await chakram.patch(project_uri, mod_proj, this.options)
    expect(patch_response).to.have.status(200)

    const get_response = await chakram.get(project_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.comprise.of.json(mod_proj)
  })

  it('POST copy a project should create a new copy of the project', async () => {
    let new_proj = tools.generate_project()
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    let copy_uri = proj_uri + 'project-copy/'
    let project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    new_proj.name += '-1'
    expect(copy_response).to.have.status(201)
    expect(copy_response).to.comprise.of.json(new_proj)
  })

  it('POST copy check on project with copy enabled should return 200', async () => {
    let new_proj = tools.generate_project()
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    let copy_uri = proj_uri + 'project-copy-check/'
    let project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    expect(copy_response).to.have.status(200)
  })

  it('POST copy check on project with copy disabled should return 404', async () => {
    let new_proj = tools.generate_project()
    new_proj.copying_enabled = false
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    let copy_uri = proj_uri + 'project-copy-check/'
    let project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    expect(copy_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/collaborators/', () => {
  let collabs_uri, collaborator, project
  let object_schema = {
    type: 'object',
    properties: {
      id: {
        type: 'string',
      },
      owner: {
        type: 'boolean',
      },
      project: {
        type: 'string',
      },
      user: {
        type: 'string',
      },
      joined: {
        type: 'string',
      },
      username: {
        type: 'string',
      },
      email: {
        type: 'string',
      },
      first_name: {
        type: 'string',
      },
      last_name: {
        type: 'string',
      },
      permissions: {
        type: 'array',
        items: {
          type: 'string',
        },
      },
    },
  }
  let array_schema = {
    type: 'array',
    items: object_schema,
  }
  //Create a user and project to be used in the tests.
  before(async () => {
    let prof_uri = tools.get_request_uri('users/profiles/')
    let new_user = {
      username: faker.internet.userName(),
      email: faker.internet.exampleEmail(),
      first_name: faker.name.firstName(),
      last_name: faker.name.lastName(),
      password: faker.internet.password(),
    }

    const user_response = await chakram.post(prof_uri, new_user, this.options)
    expect(user_response).to.have.status(201)
    collaborator = user_response.body

    collabs_uri = tools.get_request_uri(
      util.format('%s/projects/%s/collaborators/', namespace, this.shared_proj.id),
    )
  })

  it('GET all collaborators should return a list of collaborators', async () => {
    const response = await chakram.get(collabs_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(array_schema)
  })

  it('POST assign a new collaborator should return a new collaborator object', async () => {
    let new_collab = {
      owner: false,
      member: collaborator.username,
      permissions: ['read_project', 'write_project'],
    }
    const response = await chakram.post(collabs_uri, new_collab, this.options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(object_schema)
    expect(response).to.have.json('username', collaborator.username)
  })

  it('PATCH a collaborators permissions should return update the permissions', async () => {
    let new_collab = {
      owner: false,
      member: collaborator.username,
      permissions: ['read_project'],
    }
    let patch_collab = {
      owner: true,
      member: collaborator.username,
    }
    const post_response = await chakram.post(collabs_uri, new_collab, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.have.schema(object_schema)
    expect(post_response).to.have.json('username', collaborator.username)
    let collab_uri = collabs_uri + post_response.body.id + '/'

    const patch_response = await chakram.patch(collab_uri, patch_collab, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.have.json('owner', true)
  })
})

describe('{namespace}/projects/{project}/project_files/', () => {
  const object_schema = {
    type: 'object',
    properties: {
      id: {
        type: 'string',
      },
      author: {
        type: 'string',
      },
      project: {
        type: 'string',
      },
      name: {
        type: 'string',
      },
      path: {
        type: 'string',
      },
      content: {
        type: ['null', 'string'],
      },
    },
  }
  const array_schema = {
    type: 'array',
    items: object_schema,
  }

  beforeEach(async () => {
    this.file_options = {
      formData: {
        file: fs.createReadStream('./api_tests/resources/test.txt'),
      },
      headers: {
        Authorization: this.options.headers.Authorization,
        'Content-Type': 'multipart/form-data',
      },
    }
    const proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))

    let new_proj = tools.generate_project()
    const response = await chakram.post(proj_uri, new_proj, this.options)
    expect(response).to.have.status(201)
    this.files_uri = tools.get_request_uri(
      util.format('%s/projects/%s/project_files/', namespace, response.body.id),
    )
  })

  it('POST a file should create a new file object', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
  })

  it('GET all files should return a list of files', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)

    const get_response = await chakram.get(this.files_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific file should return the file', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    const get_response = await chakram.get(file_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  it('PUT a file should replace the file', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    let put_options = JSON.parse(JSON.stringify(this.file_options))
    put_options.formData.file = fs.createReadStream('./api_tests/resources/test2.txt')
    const put_response = await chakram.put(file_uri, undefined, put_options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.have.schema(object_schema)
    expect(put_response.body.name).to.equal('test2.txt')
  })

  it('PATCH a file should replace the file', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    let patch_options = JSON.parse(JSON.stringify(this.file_options))
    patch_options.formData.file = fs.createReadStream('./api_tests/resources/test2.txt')
    const patch_response = await chakram.patch(file_uri, undefined, patch_options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.have.schema(object_schema)
    expect(patch_response.body.name).to.equal('test2.txt')
  })

  it('DELETE a file should replace the file', async () => {
    const response = await chakram.post(this.files_uri, undefined, this.file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    const del_response = await chakram.delete(file_uri, undefined, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(file_uri, this.options)
    expect(get_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/servers/', () => {
  const object_schema = {
    type: 'object',
    properties: {
      id: {
        type: 'string',
      },
      name: {
        type: 'string',
      },
      created_at: {
        type: 'string',
      },
      image_name: {
        type: 'string',
      },
      server_size: {
        type: 'string',
      },
      startup_script: {
        type: 'string',
      },
      config: {
        type: 'object',
        additionalProperties: false,
        properties: {
          type: {
            type: 'string',
          },
        },
      },
      status: {
        type: 'string',
      },
      connected: {
        type: 'array',
        items: {
          $id: 'kermodebear',
          title: 'Empty Object',
          description: "This accepts anything, as long as it's valid JSON.",
        },
      },
      host: {
        type: 'null',
      },
      project: {
        type: 'string',
      },
      created_by: {
        type: 'string',
      },
      endpoint: {
        type: 'string',
      },
      logs_url: {
        type: 'string',
      },
      status_url: {
        type: 'string',
      },
    },
  }
  const array_schema = {
    type: 'array',
    items: object_schema,
  }

  it('POST a server should return a new server object', async () => {
    const server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(server)
  })

  it('GET all servers should return a list of servers', async () => {
    const server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)

    const get_response = await chakram.get(this.servers_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific server should return the server', async () => {
    const server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const get_response = await chakram.get(server_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  it('PUT a server should replace the server', async () => {
    const server = tools.generate_server(this.nano.id)
    const update_server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const put_response = await chakram.put(server_uri, update_server, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.comprise.of.json(update_server)
  })

  it('PATCH a server should update the server', async () => {
    const server = tools.generate_server(this.nano.id)
    const update_server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const patch_response = await chakram.patch(server_uri, update_server, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.comprise.of.json(update_server)
  })

  it('DELETE a server should remove the server', async () => {
    const server = tools.generate_server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const del_response = await chakram.delete(server_uri, undefined, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(server_uri, this.options)
    expect(get_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/servers/run-stats/', () => {
  before(async () => {})
})
