describe('Web Load Test', () => {
  it('it visits the webapp', () => {
    cy.visit('localhost:8080/');
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app');
  })
})

// describe('Sign Up Test', () => {
//   it('visits the register page', () => {
//     cy.get('#register').click();
//     cy.url().should('eq', 'http://localhost:8080/register-selection');
//   })
//   it('navigates to register', () => {
//     cy.get('#register-button').click();
//     cy.url().should('eq', 'http://localhost:8080/register');
//   })
//   it('has access code section', () => {
//     cy.get('#access-code').should('exist');
//   })
//   it('has access code button', () => {
//     cy.get('#access-code-button').should('exist');
//   })
//   it('enters access code', () => {
//     cy.get('#access-code').type('M@n@gr!200');
//     cy.get('#access-code-button').click();
//   })
//   it('should have navigated to register form', () => {
//     cy.url().should('eq', 'http://localhost:8080/admin-registration');
//   })
//   it('should register', () => {
//     cy.get('#company').type('Cypress Test Company');
//     cy.get('#name').type('Cypress Test');
//     cy.get('#email').type('cypress@test.com');
//     cy.get('#password').type('Password1234!');
//     cy.get('#confirm-password').type('Password1234!');
//     cy.get('#sign-up').click();
//   })
//   it('should have navigated to login', () => {
//     cy.url().should('eq', 'http://localhost:8080/login');
//   })
// })

describe('Log In Test', () => {
  it('it visits the webapp', () => {
    cy.visit('localhost:8080/');
  })
  it('visits the login page', () => {
    cy.get('#login').click();
    cy.url().should('eq', 'http://localhost:8080/login');
  })
  it('has email section', () => {
    cy.get('#emailfield').should('exist');
  })
  it('has password section', () => {
    cy.get('#passwordfield').should('exist');
  })
  it('should log in', () => {
    cy.get('#emailfield').type('cypress@test.com');
    cy.get('#passwordfield').type('Password1234!');
    cy.get('#login-button').click();
  })
  it('should redirect to summaires', () => {
    cy.url().should('eq', 'http://localhost:8080/summaries');
  })
})
