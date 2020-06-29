describe('Managr UI Tests', () => {
  it('it visits the webapp', () => {
    cy.visit('/')
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app')
  })
  it('contains a login text field', () => {
    cy.get('input')
      .should('have.attr', 'placeholder', 'email')
      .as('emailField')
  })
  it('contains a login button', () => {
    cy.get('button').contains('Next')
  })
  it('should show the password field if an exisitng email entered', () => {
    cy.get('input')
      .should('have.attr', 'placeholder', 'email')
      .as('emailField')

    cy.get('@emailField')
      .eq(0)
      .type('admin@admin.com')
    cy.get('button')
      .contains('Next')
      .click()
    cy.get('input')
      .eq(1)
      .should('have.attr', 'placeholder', 'password')
      .should('not.have.class', 'hidden')
  })
})
