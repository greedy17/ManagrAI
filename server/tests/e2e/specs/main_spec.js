describe('Managr UI Tests', () => {
  it('it visits the webapp', () => {
    cy.visit('/')
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app')
  })
  it('contains a login text field', () => {
    cy.get('input').should('have.attr', 'placeholder', 'email').as('emailField')
  })
})
