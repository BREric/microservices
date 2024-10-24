Feature: La API permite a los usuarios obtener detalles de su propio usuario

  Scenario: Obtener detalles del usuario
    Given  soy un usuario autenticado
    When hago una solicitud GET a users seguido de mi id
    Then obtengo los datos de mi usuario
    And obtengo un código de estado 200 al obtener los detalles del usuario


  Scenario: Intentar obtener detalles de otro usuario
    Given soy un usuario autenticado
    When realizo una solicitud GET a users seguido de un id de usuario diferente al mío
    Then obtengo un código de estado 404 indicando que no tengo permiso para acceder a la información de otro usuario