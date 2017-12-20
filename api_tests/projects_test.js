const chakram = require('chakram')
const util = require('util')
const config = require('./config')
const tools = require('./test_utils')
const faker = require('faker')
const expect = chakram.expect

const namespace = config.username

before(async () => {
  const token = await tools.login(config.username, config.password)
  this.options = {
    headers: {
      Authorization: util.format('%s %s', 'Bearer', token),
    },
  }
})

let generate_project = () => {
  return {
    name: faker.lorem.words(1) + faker.random.number(9999999),
    description: faker.lorem.sentence(),
    private: true,
    copying_enabled: true,
  }
}

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
    let new_proj = generate_project()
    let response = await chakram.post(proj_uri, new_proj, this.options)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(new_proj)
    this.project_id = response.body.id
  })

  it('GET all projects should return a list of projects', async () => {
    let new_proj = generate_project()
    const post_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(new_proj)
    this.project_id = post_response.body.id

    const get_response = await chakram.get(proj_uri, this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific project should return the project', async () => {
    let new_proj = generate_project()
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

  //Disabled because of issue #624
  it.skip('DELETE a project should remove the project', async () => {
    let project_uri
    let new_proj = generate_project()
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
    let new_proj = generate_project()
    let mod_proj = generate_project()
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
    let new_proj = generate_project()
    let mod_proj = generate_project()
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
    let new_proj = generate_project()
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
    let new_proj = generate_project()
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
    let new_proj = generate_project()
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
    let proj_uri = tools.get_request_uri(util.format('%s/projects/', namespace))
    let new_user = {
      username: faker.internet.userName(),
      email: faker.internet.email(),
      first_name: faker.name.firstName(),
      last_name: faker.name.lastName(),
      password: faker.internet.password(),
    }

    const user_response = await chakram.post(prof_uri, new_user, this.options)
    expect(user_response).to.have.status(201)
    collaborator = user_response.body

    let new_proj = generate_project()
    const coll_response = await chakram.post(proj_uri, new_proj, this.options)
    expect(coll_response).to.have.status(201)
    project = coll_response.body
    collabs_uri = tools.get_request_uri(
      util.format('%s/projects/%s/collaborators/', namespace, project.id),
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
