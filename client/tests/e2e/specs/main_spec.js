describe('Managr UI Tests', () => {
  it('it visits the webapp', () => {
    cy.visit('/')
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app')
  })
})
