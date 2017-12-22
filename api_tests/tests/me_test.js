const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const generator = require('../generator')
const expect = chakram.expect

const teams_uri = tools.get_request_uri('me/teams/')

describe('me', () => {
  const me_schema = tools.get_schema('me', 'me/')

  it('GET should return me', async () => {
    const uri = tools.get_request_uri('me')
    const response = await chakram.get(uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(me_schema)
    expect(response).to.have.json('username', config.username)
    expect(response).to.have.json('email', config.email)
    expect(response).to.have.header('content-type', 'application/json')
  })
})

describe('me/teams', () => {
  beforeEach(() => {
    this.team_json = generator.team()
  })
  afterEach(async () => {
    if (this.team) {
      const response = await chakram.delete(teams_uri + this.team + '/', {})
      this.team = undefined
      expect(response).to.have.status(204)
    }
  })

  it('POST a valid team should create a new team', async () => {
    const response = await chakram.post(teams_uri, this.team_json)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(this.team_json)
    this.team = response.body.name
    const uri = teams_uri + this.team_json.name

    const get_response = await chakram.get(uri)
    expect(get_response).to.have.status(200)
    expect(get_response).to.comprise.of.json(this.team_json)
  })

  it('DELETE an existing team should remove the team', async () => {
    const uri = teams_uri + this.team_json.name + '/'
    const response = await chakram.post(teams_uri, this.team_json)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(this.team_json)

    const del_response = await chakram.delete(uri, {})
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(uri)
    expect(get_response).to.have.status(404)
  })

  it('PATCH an existing team should modify a team', async () => {
    let modified_team = JSON.parse(JSON.stringify(this.team_json))
    const response = await chakram.post(teams_uri, this.team_json)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(this.team_json)
    const uri = teams_uri + this.team_json.name + '/'
    modified_team.name = 'TestTeam123'

    const patch_response = await chakram.patch(uri, modified_team)
    expect(patch_response).to.have.status(200)
    this.team = modified_team.name
    expect(patch_response).to.comprise.of.json(modified_team)
  })

  it('PUT an existing team should modify a team', async () => {
    let modified_team = JSON.parse(JSON.stringify(this.team_json))
    const response = await chakram.post(teams_uri, this.team_json)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(this.team_json)
    const uri = teams_uri + this.team_json.name + '/'
    modified_team.name = 'TestTeam123'

    const put_response = await chakram.put(uri, modified_team)
    expect(put_response).to.have.status(200)
    this.team = modified_team.name
    expect(put_response).to.comprise.of.json(modified_team)
  })
})

describe('me/teams/{team}/groups', () => {
  before(async () => {
    this.team_json = generator.team()
    const response = await chakram.post(teams_uri, this.team_json)
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(this.team_json)
    this.uri = tools.get_request_uri('me/teams')
    this.uri = util.format('%s/%s/groups/', this.uri, this.team_json.name)
    this.team_json = response.body
  })

  after(async () => {
    const response = await chakram.delete(teams_uri + this.team_json.name + '/', {})
    expect(response).to.have.status(204)
  })

  it('GET groups should return a list of groups', async () => {
    const schema = tools.get_schema('me', 'groups/')
    const response = await chakram.get(this.uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
  })

  it('POST a group should return a valid group', async () => {
    const group = generator.group()
    const response = await chakram.get(this.uri)
    expect(response).to.have.status(200)
    const group_parent = response.body[0].name
    group.parent = response.body[0].id

    const post_response = await chakram.post(this.uri, group)
    group.parent = group_parent
    expect(post_response).to.have.status(201)
    expect(post_response).to.comprise.of.json(group)
  })
})
