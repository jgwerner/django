const faker = require('faker')

module.exports = class Generator {
  static trigger() {
    return {
      name: faker.lorem.words(3).replace(' ', ''),
      webhook: {
        url: faker.internet.url(),
        payload: {},
      },
    }
  }

  static ssh_tunnel() {
    return {
      name: faker.lorem.words(1) + faker.random.number(9999999),
      host: faker.internet.url(),
      local_port: faker.random.number(65535),
      remote_port: faker.random.number(65535),
      endpoint: faker.internet.url(),
      username: faker.name.firstName() + faker.name.lastName(),
    }
  }

  static server(server_size) {
    return {
      name: faker.lorem.words(1) + faker.random.number(99999),
      image_name: 'datascience-notebook',
      server_size: server_size,
      config: {
        type: 'restful',
      },
    }
  }

  static project() {
    return {
      name: faker.lorem.words(1) + faker.random.number(9999999),
      description: faker.lorem.sentence(),
      private: true,
      copying_enabled: true,
    }
  }

  static user() {
    return {
      username: faker.name.firstName() + '_' + faker.random.number(9999999),
      email: faker.internet.exampleEmail(),
      first_name: faker.name.firstName(),
      last_name: faker.name.lastName(),
      password: faker.internet.password(),
      profile: {
        bio: faker.lorem.sentence(),
        location: faker.address.country(),
        company: faker.company.companyName(),
      },
    }
  }

  static team() {
    return {
      name: faker.lorem.words(1),
      description: faker.lorem.sentence(),
      website: faker.internet.url(),
      location: faker.address.country(),
    }
  }

  static group() {
    return {
      name: faker.lorem.words(1),
      permissions: [],
      private: true,
      parent: '',
    }
  }

  static credit_card() {
    return {
      name: faker.lorem.words(1),
      address_line1: faker.address.streetAddress(),
      address_city: faker.address.city(),
      address_state: faker.address.state(),
      address_zip: faker.address.zipCode(),
      address_country: faker.address.country(),
    }
  }

  static email() {
    return {
      address: faker.internet.exampleEmail(),
      public: true,
      unsubscribed: true,
    }
  }
}
