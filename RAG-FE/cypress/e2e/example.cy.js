describe('Recall document management', () => {
  it('requires confirmation before deleting a document', () => {
    cy.intercept('GET', '**/api/documents/', {
      statusCode: 200,
      body: {
        documents: [{ filename: 'example.pdf', status: 'indexed', chunks: 2, error: '' }],
      },
    }).as('listDocuments')
    cy.intercept('DELETE', '**/api/documents/example.pdf/').as('deleteDocument')

    cy.visit('/')
    cy.wait('@listDocuments')
    cy.contains('example.pdf').should('be.visible')

    cy.on('window:confirm', (message) => {
      expect(message).to.contain('example.pdf')
      return false
    })

    cy.contains('button', 'Delete').click()
    cy.get('@deleteDocument.all').should('have.length', 0)
  })
})
