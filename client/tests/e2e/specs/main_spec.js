describe('Web Load Test', () => {
  it('it visits the webapp', () => {
    cy.visit('localhost:8080/');
  })
  it('mounts the vue app', () => {
    cy.get('div').should('have.id', 'app');
  })
})

// describe('Log In Test', () => {
//   it('visits the webapp', () => {
//     cy.visit('localhost:8080/');
//   })
//   it('visits the login page', () => {
//     cy.get('#login').click();
//     cy.url().should('eq', `http://localhost:8080/login`);
//   })
//   it('has email section', () => {
//     cy.get('#emailfield').should('exist');
//   })
//   it('has password section', () => {
//     cy.get('#passwordfield').should('exist');
//   })
//   it('should log in', () => {
//     cy.get('#emailfield').type('cypress@test.com');
//     cy.get('#passwordfield').type('Password1234!');
//     cy.get('#login-button').click();
//   })
//   it('should redirect to summaires', () => {
//     cy.url().should('eq', 'http://localhost:8080/summaries');
//   })
// })

// describe('Summarize Page Test', () => {
//   it('be PRO', () => {
//     cy.get('#pro-free-version').should('have.text', 'PRO');
//   })
//   it('have Summarize, Pitch, and Transcribe options', () => {
//     cy.get('#router-summarize').should('exist');
//     cy.get('#router-pitch').should('exist');
//     cy.get('#router-transcribe1').should('exist');
//   })
//   it('has News, Social, and Articles tabs', () => {
//     cy.get('#news-tab').should('exist');
//     cy.get('#social-tab').should('exist');
//     cy.get('#articles-tab').should('exist');
//   })
//   it('has search input', () => {
//     cy.get('#search-input').should('exist');
//   })
//   it('uses the search input', () => {
//     cy.get('#search-input').type('Bread');
//   })
//   it('has instructions input', () => {
//     cy.get('#instructions').should('exist');
//   })
//   it('selects an instruction', () => {
//     cy.get('#instructions-text-area').click();
//     cy.get('.dropdown-item:first').click();
//     cy.get('#instructions-text-area').should('have.value', 'Summarize the news');
//   })
//   it('has generate button', () => {
//     cy.get('#generate-summary').should('exist');
//   })
// })
