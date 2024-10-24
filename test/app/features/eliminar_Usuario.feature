Feature: La API permite a los usuarios eliminar su cuenta

    Scenario: Yo como usuario no autenticado quiero eliminar mi cuenta
        Given Soy un usuario no autenticado para eliminar mi cuenta
        When invoco el servicio de eliminación de mi cuenta sin autenticar
        Then obtengo un código de estado 401 al intentar eliminar mi cuenta sin autenticar

    Scenario: Yo como usuario quiero eliminar una cuenta que no es la mía
        Given Soy un usuario autenticado para eliminar otra cuenta
        When realizo la solicitud de eliminación de una cuenta diferente
        Then obtengo un código de estado 404 al intentar eliminar una cuenta diferente

    Scenario: Yo como usuario quiero eliminar mi cuenta
        Given Soy un usuario autenticado para eliminar mi cuenta
        When invoco el servicio de eliminación de mi cuenta
        Then obtengo un código de estado 204 que me indica que fue exitosa
