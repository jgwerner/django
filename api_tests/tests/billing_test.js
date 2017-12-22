const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const generator = require('../generator')
const expect = chakram.expect

const namespace = config.username

describe('{namespace}/billing/cards/', () => {
  const cards_uri = tools.get_request_uri(util.format('%s/billing/cards/', namespace))
  const token = {
    token: 'tok_visa',
  }
  const object_schema = tools.get_schema('billing', 'cards/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }

  it('POST creating a new credit card should return a valid credit card', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    expect(response).to.have.json('brand', 'Visa')
  })

  it('DELETE specific card should delete the card', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    const card_uri = cards_uri + response.body.id + '/'

    const del_response = await chakram.delete(card_uri, {})
    expect(del_response).to.have.status(204)
  })

  it('GET all cards should return a list of credit cards', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    const get_response = await chakram.get(cards_uri)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(array_schema)
  })

  it('GET specific card should return a credit card', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    const card_uri = cards_uri + response.body.id + '/'

    const get_response = await chakram.get(card_uri)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  const updated_card = generator.credit_card()

  it('PUT update a credit card should return the new card', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    const card_uri = cards_uri + response.body.id + '/'

    const put_response = await chakram.put(card_uri, updated_card)
    expect(put_response).to.have.status(200)
    expect(put_response).to.comprise.of.json(updated_card)
  })

  it('PATCH update a credit card should return the new card', async () => {
    const response = await chakram.post(cards_uri, token)
    expect(response).to.have.status(201)
    const card_uri = cards_uri + response.body.id + '/'

    const patch_response = await chakram.patch(card_uri, updated_card)
    expect(patch_response).to.have.status(200)
    expect(patch_response).to.comprise.of.json(updated_card)
  })
})

describe('{namespace}/billing/invoice/', async () => {
  const invoice_uri = tools.get_request_uri(util.format('%s/billing/invoices/', namespace))

  it('GET invoices should return a list of invoices', async () => {
    const response = await chakram.get(invoice_uri)
    //Not sure how to seed invoices for proper testing so for now just expect 200
    expect(response).to.have.status(200)
  })
})

describe('{namespace}/billing/plans/', async () => {
  const plans_uri = tools.get_request_uri(util.format('%s/billing/plans/', namespace))
  const object_schema = tools.get_schema('billing', 'plans/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }

  it('GET plans should return a list of plans', async () => {
    const response = await chakram.get(plans_uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(array_schema)
  })

  it('GET specific plan should return the plan', async () => {
    const response = await chakram.get(plans_uri)
    expect(response).to.have.status(200)
    const plan_uri = plans_uri + response.body[0].id + '/'

    const get_response = await chakram.get(plan_uri)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })
})

describe('{namespace}/billing/subscriptions/', async () => {
  const subscriptions_uri = tools.get_request_uri(
    util.format('%s/billing/subscriptions/', namespace),
  )
  const object_schema = tools.get_schema('billing', 'subscriptions/')
  const array_schema = {
    type: 'array',
    items: object_schema,
  }
  let plan

  before(async () => {
    const plans_uri = tools.get_request_uri(util.format('%s/billing/plans/', namespace))
    const response = await chakram.get(plans_uri)
    expect(response).to.have.status(200)
    plan = { plan: response.body[0].id }
  })

  it('GET subscriptions should return a list of subscriptions', async () => {
    const response = await chakram.get(subscriptions_uri)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(array_schema)
  })

  it('GET specific subscription should return the subscription', async () => {
    const response = await chakram.get(subscriptions_uri)
    expect(response).to.have.status(200)
    const subscription_uri = subscriptions_uri + response.body[0].id + '/'

    const get_response = await chakram.get(subscription_uri)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(object_schema)
  })

  it('PUT a new subscription should create the new subscription', async () => {
    const response = await chakram.post(subscriptions_uri, plan)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(object_schema)
  })

  it('DELETE a subscription should delete the subscription', async () => {
    const response = await chakram.post(subscriptions_uri, plan)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(object_schema)
    const subscription_uri = subscriptions_uri + response.body.id + '/'

    const del_response = await chakram.delete(subscription_uri, {})
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(subscription_uri)
    expect(get_response).to.have.status(404)
  })
})
