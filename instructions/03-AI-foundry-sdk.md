---
lab:
    title: 'Crear una aplicación de chat con IA generativa'
    description: 'Aprende cómo usar el Azure AI Foundry SDK para construir una aplicación que se conecta a tu proyecto y conversa con un modelo de lenguaje.'
    time: '30 min'
---

# Crear una aplicación de chat con IA generativa

En este ejercicio, utilizarás el Azure AI Foundry SDK para crear una aplicación de chat sencilla que se conecta a un proyecto y conversa con un modelo de lenguaje.

Este ejercicio tiene una duración aproximada de **30** minutos.

## Crear un proyecto Azure AI Foundry

Comencemos creando un proyecto en Azure AI Foundry.

1. En un navegador web, abre el [portal Azure AI Foundry](https://ai.azure.com) en `https://ai.azure.com` e inicia sesión usando tus credenciales de Azure. Cierra cualquier sugerencia o panel de inicio rápido que se abra la primera vez que inicies sesión y, si es necesario, utiliza el logo de **Azure AI Foundry** en la esquina superior izquierda para navegar a la página de inicio, que se verá similar a la siguiente imagen:

    ![Captura de pantalla del portal Azure AI Foundry.](./media/ai-foundry-home.png)

2. En la página de inicio, selecciona **+ Crear proyecto**.
3. En el asistente **Crear un proyecto**, introduce un nombre adecuado para el proyecto (por ejemplo, `my-ai-project`) y revisa los recursos de Azure que se crearán automáticamente para soportar tu proyecto.
4. Selecciona **Personalizar** y especifica la siguiente configuración para tu hub:
    - **Nombre del hub**: *Un nombre único - por ejemplo, `my-ai-hub`*
    - **Suscripción**: *Tu suscripción de Azure*
    - **Grupo de recursos**: *Crea un nuevo grupo de recursos con un nombre único (por ejemplo, `my-ai-resources`), o selecciona uno existente*
    - **Ubicación**: Elige una región al azar de la siguiente lista\*:
        - East US
        - East US 2
        - North Central US
        - South Central US
        - Sweden Central
        - West US
        - West US 3
    - **Conectar Azure AI Services o Azure OpenAI**: *Crea un nuevo recurso de AI Services con un nombre adecuado (por ejemplo, `my-ai-services`) o utiliza uno existente*
    - **Conectar Azure AI Search**: Omitir conexión

    > \* Las cuotas del modelo están limitadas a nivel de inquilino por cuotas regionales. Elegir una región al azar ayuda a distribuir la disponibilidad de cuotas cuando varios usuarios trabajan en el mismo inquilino. En caso de que se alcance el límite de cuota más adelante en el ejercicio, podría ser necesario crear otro recurso en una región diferente.

5. Selecciona **Siguiente** y revisa tu configuración. Luego selecciona **Crear** y espera a que el proceso se complete.
6. Una vez creado el proyecto, cierra cualquier sugerencia que se muestre y revisa la página del proyecto en el portal Azure AI Foundry, que debería verse similar a la siguiente imagen:

    ![Captura de pantalla de los detalles de un proyecto Azure AI en el portal Azure AI Foundry.](./media/ai-foundry-project.png)

## Desplegar un modelo de IA generativa

Ahora estás listo para desplegar un modelo de lenguaje de IA generativa que soporte tu aplicación de chat. En este ejemplo, usarás el modelo Microsoft Phi-4; pero los principios son los mismos para cualquier modelo.

1. En la barra de herramientas en la esquina superior derecha de la página del proyecto en Azure AI Foundry, utiliza el icono de **Funciones de vista previa** para habilitar la función **Desplegar modelos en el servicio de inferencia de modelos Azure AI**. Esta función asegura que el despliegue de tu modelo esté disponible en el servicio de inferencia Azure AI, que usarás en el código de tu aplicación.
2. En el panel izquierdo de tu proyecto, en la sección **Mis activos**, selecciona la página **Modelos + endpoints**.
3. En la pestaña **Despliegues de modelos** de la página **Modelos + endpoints**, en el menú **+ Desplegar modelo**, selecciona **Desplegar modelo base**.
4. Busca el modelo **Phi-4** en la lista, y luego selecciónalo y confírmalo.
5. Acepta el acuerdo de licencia si se solicita, y luego despliega el modelo con la siguiente configuración seleccionando **Personalizar** en los detalles del despliegue:
    - **Nombre del despliegue**: *Un nombre único para el despliegue de tu modelo - por ejemplo, `phi-4-model` (recuerda el nombre que asignes, lo necesitarás más tarde)*
    - **Tipo de despliegue**: Estándar global
    - **Detalles del despliegue**: *Utiliza la configuración predeterminada*
6. Espera a que el estado de provisión del despliegue llegue a **Completado**.

## Crear una aplicación cliente para chatear con el modelo

Ahora que has desplegado un modelo, puedes utilizar el Azure AI Foundry SDK para desarrollar una aplicación que converse con él.

### Edita las variables de ambiente
Edita el archivo [.sample-env](../lab/chat-app/.sample-env) con los valores correspondientes.
Despues, cambia el nombre de [.sample-env] a [.env]

### Escribir código para conectar el proyecto y conversar con el modelo

> **Consejo**: A medida que agregues código en el archivo Python, asegúrate de mantener la indentación correcta.

1. Ingresa el siguiente comando para editar el archivo de código Python [**chat-app.py**](../lab/chat-app/chat-app.py) que se proporcionó:


2. En el archivo de código, observa las declaraciones **import** que se han añadido al inicio del archivo. Luego, debajo del comentario **# Add AI Projects reference**, añade el siguiente código para referenciar la librería Azure AI Projects:

    ```python
   from azure.ai.projects import AIProjectClient
    ```

3. En la función **main**, bajo el comentario **# Get configuration settings**, observa que el código carga los valores de cadena de conexión del proyecto y el nombre del despliegue del modelo definidos en el archivo **.env**.
4. Bajo el comentario **# Initialize the project client**, añade el siguiente código para conectar tu proyecto Azure AI Foundry usando las credenciales de Azure con las que estás autenticado actualmente:

    ```python
   project = AIProjectClient.from_connection_string(
        conn_str=project_connection,
        credential=DefaultAzureCredential()
        )
    ```
    
5. Bajo el comentario **# Get a chat client**, añade el siguiente código para crear un objeto cliente para conversar con un modelo:

    ```python
   chat = project.inference.get_chat_completions_client()
    ```

6. Observa que el código incluye un bucle que permite al usuario ingresar un mensaje hasta que escriba "quit". Luego, en la sección del bucle, bajo el comentario **# Get a chat completion**, añade el siguiente código para enviar el mensaje y recuperar la respuesta de tu modelo:

    ```python
   response = chat.complete(
        model=model_deployment,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that answers questions."},
            {"role": "user", "content": input_text},
            ],
        )
   print(response.choices[0].message.content)
    ```

7. Utiliza el comando **CTRL+S** para guardar los cambios en el archivo de código 

### Ejecutar la aplicación de chat

1. En el panel de línea de comandos de la Cloud Shell, ingresa el siguiente comando para ejecutar el código Python:

```bash
python lab/chat-app/chat-app.py
```

2. Cuando se te pida, ingresa una pregunta, por ejemplo, `¿Cuál es el animal más rápido de la Tierra?` y revisa la respuesta de tu modelo de IA generativa.
3. Prueba con algunas preguntas más. Cuando hayas terminado, escribe `quit` para salir del programa.

## Resumen

En este ejercicio, utilizaste el Azure AI Foundry SDK para crear una aplicación cliente para un modelo de IA generativa que desplegaste en un proyecto Azure AI Foundry.

## Limpieza

Si has terminado de explorar el portal Azure AI Foundry, deberías eliminar los recursos que creaste en este ejercicio para evitar incurrir en costos innecesarios de Azure.

1. Regresa a la pestaña del navegador que contiene el portal Azure (o reabre el [portal Azure](https://portal.azure.com) en una nueva pestaña) y visualiza el contenido del grupo de recursos donde desplegaste los recursos usados en este ejercicio.
2. En la barra de herramientas, selecciona **Eliminar grupo de recursos**.
3. Ingresa el nombre del grupo de recursos y confirma que deseas eliminarlo.