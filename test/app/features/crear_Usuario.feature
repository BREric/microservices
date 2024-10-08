Feature: La API permite a los usuarios crear un nuevo usuario

    Scenario: Yo como usuario quiero crear un nuevo usuario con datos válidos
        Given Tengo un nombre de usuario, email y contraseña válidos
        When invoco el servicio de creación de usuario con los datos
        Then obtengo un código de estado 201

    Scenario: Intentar crear un usuario con nombre de usuario ya registrado
        Given Tengo un nombre de usuario ya está registrado
        When invoco el servicio de creación de usuario con el nombre de usuario
        Then obtengo un código de estado 409 indicando conflicto
        And un mensaje que indique que el nombre de usuario ya está en uso

    Scenario: Intentar crear un usuario sin proporcionar un nombre de usuario
        Given No ingreso un nombre de usuario
        When invoco el servicio de creación de usuario
        Then obtengo un código de estado 400 indicando error en la solicitud
