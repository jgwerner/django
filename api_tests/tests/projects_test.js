const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const generator = require('../generator')
const fs = require('fs')
const path = require('path')
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
  const shared_proj = generator.project()

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
  const server = generator.server(this.nano.id)
  const server_response = await chakram.post(this.servers_uri, server, this.options)
  expect(response).to.have.status(201)
  this.shared_server = server_response.body

  console.log('Shared Project: %s', this.shared_proj.id)
  console.log('Shared Server: %s', this.shared_server.id)
})

describe('{namespace}/projects/', () => {
  let proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))
  let object_schema = tools.get_schema('projects', 'projects/')
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
    let new_proj = generator.project()
    let response = await chakram.post(proj_uri, new_proj, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(new_proj)
    this.project_id = response.body.id
  })

  it('GET all projects should return a list of projects', async () => {
    let new_proj = generator.project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    this.project_id = post_response.body.id

    const get_response = await chakram.get(proj_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific project should return the project', async () => {
    let new_proj = generator.project()
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
    const new_proj = generator.project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    const project_uri = proj_uri + response.body.id + '/'

    const delete_response = await chakram.delete(project_uri, {}, this.options)
    expect(delete_response).to.have.status(204)

    const get_response = await chakram.get(project_uri, this.options)
    expect(get_response).to.have.status(404)
  })

  it('PUT a project should replace the project', async () => {
    const new_proj = generator.project()
    const mod_proj = generator.project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    const uri = proj_uri + post_response.body.id + '/'

    const put_response = await chakram.put(uri, mod_proj, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.comprise.of.json(mod_proj)
  })

  it('PATCH a project should replace the project', async () => {
    const new_proj = generator.project()
    const mod_proj = generator.project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    const project_uri = proj_uri + post_response.body.id + '/'

    const patch_response = await chakram.patch(project_uri, mod_proj, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.comprise.of.json(mod_proj)
  })

  it('POST copy a project should create a new copy of the project', async () => {
    let new_proj = generator.project()
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    const copy_uri = proj_uri + 'project-copy/'
    const project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    new_proj.name += '-1'
    expect(copy_response).to.have.status(201)
    expect(copy_response).to.comprise.of.json(new_proj)
  })

  it('POST copy check on project with copy enabled should return 200', async () => {
    const new_proj = generator.project()
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    const copy_uri = proj_uri + 'project-copy-check/'
    const project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    expect(copy_response).to.have.status(200)
  })

  it('POST copy check on project with copy disabled should return 404', async () => {
    let new_proj = generator.project()
    new_proj.copying_enabled = false
    const proj_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(proj_response).to.have.status(201)
    expect(proj_response).to.comprise.of.json(new_proj)
    this.project_id = proj_response.body.id
    const copy_uri = proj_uri + 'project-copy-check/'
    const project = { project: this.project_id }

    const copy_response = await chakram.post(copy_uri, project, this.options)
    expect(copy_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/collaborators/', () => {
  let collabs_uri, collaborator, project
  let object_schema = tools.get_schema('projects', 'collaborators/')
  let array_schema = {
    type: 'array',
    items: object_schema,
  }
  //Create a user and project to be used in the tests.
  before(async () => {
    let prof_uri = tools.get_request_uri('users/profiles/')
    let new_user = generator.user()

    // collab test need their own project to not affect other tests
    const proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))
    const collab_proj = generator.project()

    const proj_response = await chakram.post(proj_uri, collab_proj, this.options)
    expect(proj_response).to.have.status(201)

    const user_response = await chakram.post(prof_uri, new_user, this.options)
    expect(user_response).to.have.status(201)
    collaborator = user_response.body

    collabs_uri = tools.get_request_uri(
      util.format('%s/projects/%s/collaborators/', namespace, proj_response.body.id),
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
  const object_schema = tools.get_schema('projects', 'project_files/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }
  const file1 = path.resolve(__dirname, '../resources/', 'test.txt')
  const file2 = path.resolve(__dirname, '../resources/', 'test2.txt')
  console.log(file1)
  console.log(file2)

  before(async () => {
    this.headers = {
      Authorization: this.options.headers.Authorization,
      'Content-Type': 'multipart/form-data',
    }
    this.files_uri = tools.get_request_uri(
      util.format('%s/projects/%s/project_files/', namespace, this.shared_proj.id),
    )
  })

  it('POST a file should create a new file object', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    console.log(file_options.formData.file)
    const response = await chakram.post(this.files_uri, undefined, file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
  })

  it('GET all files should return a list of files', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    const response = await chakram.post(this.files_uri, undefined, file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)

    const get_response = await chakram.get(this.files_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific file should return the file', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    const response = await chakram.post(this.files_uri, undefined, file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    const get_response = await chakram.get(file_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  it('PUT a file should replace the file', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    const response = await chakram.post(this.files_uri, undefined, file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    let put_options = JSON.parse(JSON.stringify(file_options))
    put_options.formData.file = fs.createReadStream(file2)
    const put_response = await chakram.put(file_uri, undefined, put_options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.have.schema(object_schema)
    expect(put_response.body.name).to.contain('test2')
  })

  it('PATCH a file should replace the file', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    const response = await chakram.post(this.files_uri, undefined, file_options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(array_schema)
    const file_uri = util.format('%s%s/', this.files_uri, response.body[0].id)

    let patch_options = JSON.parse(JSON.stringify(file_options))
    patch_options.formData.file = fs.createReadStream(file2)
    const patch_response = await chakram.patch(file_uri, undefined, patch_options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.have.schema(object_schema)
    expect(patch_response.body.name).to.contain('test2')
  })

  it('DELETE a file should replace the file', async () => {
    const file_options = {
      formData: {
        file: fs.createReadStream(file1),
      },
      headers: this.headers,
    }
    const response = await chakram.post(this.files_uri, undefined, file_options)
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
  const object_schema = tools.get_schema('projects', 'servers/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }

  it('POST a server should return a new server object', async () => {
    const server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(server)
  })

  it('GET all servers should return a list of servers', async () => {
    const server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)

    const get_response = await chakram.get(this.servers_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific server should return the server', async () => {
    const server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const get_response = await chakram.get(server_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  it('PUT a server should replace the server', async () => {
    const server = generator.server(this.nano.id)
    const update_server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const put_response = await chakram.put(server_uri, update_server, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.comprise.of.json(update_server)
  })

  it('PATCH a server should update the server', async () => {
    const server = generator.server(this.nano.id)
    const update_server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const patch_response = await chakram.patch(server_uri, update_server, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.comprise.of.json(update_server)
  })

  it('DELETE a server should remove the server', async () => {
    const server = generator.server(this.nano.id)
    const response = await chakram.post(this.servers_uri, server, this.options)
    expect(response).to.have.status(201)
    const server_uri = this.servers_uri + response.body.id + '/'

    const del_response = await chakram.delete(server_uri, undefined, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(server_uri, this.options)
    expect(get_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/servers/{server}/run-stats/', () => {
  // https://github.com/3Blades/openapi/issues/186
})

describe('{namespace}/projects/{project}/servers/{server}/ssh-tunnels/', () => {
  const object_schema = tools.get_schema('projects', 'ssh-tunnels/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }
  before(() => {
    this.tunnels_uri = tools.get_request_uri(
      util.format(
        '%s/projects/%s/servers/%s/ssh-tunnels/',
        namespace,
        this.shared_proj.id,
        this.shared_server.id,
      ),
    )
  })
  it('POST a SSH tunnel should add a new SSH tunnel', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(ssh_tunnel)
    expect(response).to.have.schema(object_schema)
  })
  it('GET all tunnels should return a list of tunnels', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)

    const get_response = await chakram.get(this.tunnels_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })
  it('GET specific tunnel should return the tunnel', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)
    const tunnel_uri = this.tunnels_uri + response.body.id + '/'

    const get_response = await chakram.get(tunnel_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
    expect(get_response).to.comprise.of.json(ssh_tunnel)
  })
  it('PUT a modified tunnel should replace the existing tunnel', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const put_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)
    const tunnel_uri = this.tunnels_uri + response.body.id + '/'

    const put_response = await chakram.put(tunnel_uri, put_tunnel, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.have.schema(object_schema)
    expect(put_response).to.comprise.of.json(put_tunnel)
  })
  it('PATCH a modified tunnel should update the existing tunnel', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const patch_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)
    const tunnel_uri = this.tunnels_uri + response.body.id + '/'

    const patch_response = await chakram.patch(tunnel_uri, patch_tunnel, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.have.schema(object_schema)
    expect(patch_response).to.comprise.of.json(patch_tunnel)
  })
  it('DELETE a tunnel should remove the tunnel', async () => {
    const ssh_tunnel = generator.ssh_tunnel()
    const response = await chakram.post(this.tunnels_uri, ssh_tunnel, this.options)
    expect(response).to.have.status(201)
    const tunnel_uri = this.tunnels_uri + response.body.id + '/'

    const del_response = await chakram.delete(tunnel_uri, {}, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(tunnel_uri, this.options)
    expect(get_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/servers/{server}/triggers/', () => {
  const object_schema = tools.get_schema('projects', 'triggers/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }
  before(() => {
    this.triggers_uri = tools.get_request_uri(
      util.format(
        '%s/projects/%s/servers/%s/triggers/',
        namespace,
        this.shared_proj.id,
        this.shared_server.id,
      ),
    )
  })
  it('POST a trigger should return a new trigger', async () => {
    const trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(trigger)
    expect(response).to.have.schema(object_schema)
  })
  it('GET all triggers should a list of triggers', async () => {
    const trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)

    const get_response = await chakram.get(this.triggers_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })
  it('GET specific trigger should return the trigger', async () => {
    const trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)
    const trigger_uri = this.triggers_uri + response.body.id + '/'

    const get_response = await chakram.get(trigger_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
    expect(get_response).to.comprise.of.json(trigger)
  })
  it('PUT a modified trigger should replace the trigger', async () => {
    const trigger = generator.trigger()
    const put_trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)
    const trigger_uri = this.triggers_uri + response.body.id + '/'

    const put_response = await chakram.put(trigger_uri, put_trigger, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).to.have.schema(object_schema)
    expect(put_response).to.comprise.of.json(put_trigger)
  })
  it('PATCH a modified trigger should update the trigger', async () => {
    const trigger = generator.trigger()
    const patch_trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)
    const trigger_uri = this.triggers_uri + response.body.id + '/'

    const patch_response = await chakram.patch(trigger_uri, patch_trigger, this.options)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.have.schema(object_schema)
    expect(patch_response).to.comprise.of.json(patch_trigger)
  })
  it('DELETE a trigger should remove the trigger', async () => {
    const trigger = generator.trigger()
    const response = await chakram.post(this.triggers_uri, trigger, this.options)
    expect(response).to.have.status(201)
    const trigger_uri = this.triggers_uri + response.body.id + '/'

    const del_response = await chakram.delete(trigger_uri, {}, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(trigger_uri, this.options)
    expect(get_response).to.have.status(404)
  })
})

describe('{namespace}/projects/{project}/servers/{server}/api-key/', () => {
  const schema = tools.get_schema('projects', 'api-key/')
  before(() => {
    this.key_uri = tools.get_request_uri(
      util.format(
        '%s/projects/%s/servers/%s/api-key/',
        namespace,
        this.shared_proj.id,
        this.shared_server.id,
      ),
    )
  })
  it('GET api-key should return a valid token', async () => {
    const response = await chakram.get(this.key_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
  })
  it('POST reset api-key shourl return a new valid token', async () => {
    const refresh_uri = this.key_uri + 'reset/'
    const response = await chakram.post(refresh_uri, undefined, this.options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(schema)
  })
  it('POST verify a token should return 200', async () => {
    const response = await chakram.get(this.key_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
    const token = response.body
    const verify_uri = this.key_uri + 'auth/'

    const verify_response = await chakram.post(verify_uri, token, this.options)
    expect(response).to.have.status(200)
  })
})
