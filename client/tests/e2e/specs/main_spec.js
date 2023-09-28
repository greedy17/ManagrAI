describe('Managr UI Tests', () => {
  it('it visits the webapp', () => {
    cy.visit('localhost:8080/')
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app')
  })
  it('visits the login page', () => {
    cy.visit('localhost:8080/login')
  })
  it('has email section', () => {
    cy.get('#emailfield').should('exist');
  })
  it('has password section', () => {
    cy.get('#passwordfield').should('exist');
  })
})
