---
lab:
    title: 'Crear una aplicación de IA generativa que utiliza tus propios datos'
    description: 'Aprende cómo utilizar el modelo Retrieval Augmented Generation (RAG) para construir una aplicación de chat que base las solicitudes en tus propios datos.'
---

# Crear una aplicación de IA generativa que utiliza tus propios datos

Retrieval Augmented Generation (RAG) es una técnica utilizada para construir aplicaciones que integran datos de fuentes personalizadas en una solicitud para un modelo de IA generativa. RAG es un patrón común para desarrollar aplicaciones de IA generativa: aplicaciones de chat que utilizan un modelo de lenguaje para interpretar las entradas y generar respuestas apropiadas.

En este ejercicio, utilizarás el portal Azure AI Foundry para integrar datos personalizados en un flujo de solicitud de IA generativa.

Este ejercicio toma aproximadamente **45** minutos.

## Crear un recurso de Azure AI Search

La solución de tu aplicación de IA generativa integrará datos personalizados en un flujo de solicitud. Para apoyar esta integración, necesitarás un recurso de Azure AI Search con el que indexar tus datos.

1. En un navegador web, abre el [portal de Azure](https://portal.azure.com) en `https://portal.azure.com` e inicia sesión con tus credenciales de Azure.
2. En la página principal, selecciona **+ Crear un recurso** y busca `Azure AI Search`. Luego, crea un nuevo recurso de Azure AI Search con la siguiente configuración:

    - **Subscription**: *Selecciona tu suscripción de Azure*
    - **Resource group**: *Selecciona o crea un grupo de recursos*
    - **Service name**: *Ingresa un nombre de servicio único*
    - **Location**: *Haz una elección **aleatoria** entre alguna de las siguientes regiones*\*
        - Australia East
        - Canada East
        - East US
        - East US 2
        - France Central
        - Japan East
        - North Central US
        - Sweden Central
        - Switzerland 
    - **Pricing tier**: Basic

3. Espera a que se complete el despliegue de tu recurso de Azure AI Search.

## Crear un proyecto de Azure OpenAI Service

Ahora estás listo para crear un recurso en Azure OpenAI Service 

1. En un navegador web, abre [Azure OpenAI Service](https://portal.azure.com) e inicia sesión con tus credenciales de Azure.
2. En la página principal, selecciona **+ Create a resource**.
3. En el asistente crea un recurso de **Azure OpenAI** y personaliza:
    - **Subscription**: *Tu suscripción de Azure*
    - **Resource group**: *Selecciona el grupo de recursos que contiene tu recurso de Azure OpenAI*
    - **Location**: *Selecciona la region de tu recurso*
    - **Name**: (Nuevo) *Nombre del recurso*
    - **Pricing Tear**: *Standard SO*
4. Selecciona **Siguiente** y revisa tu configuración.
5. Selecciona **Crear** y espera a que el proceso se complete.

## Desplegar modelos

Necesitas dos modelos para implementar tu solución:

- Un modelo de *embedding* para vectorizar datos de texto y facilitar una indexación eficiente.
- Un modelo que pueda generar respuestas en lenguaje natural basadas en tus datos.

1. En el portal Azure OpenAI Service, selecciona la página **Go to AzureAI Foundry Portal**.
2. Selecciona **Deployments**
3. Crea un nuevo despliegue del modelo **text-embedding-3-large** con la siguiente configuración, seleccionando **Personalizar** en el asistente de despliegue:
    - **Deployment name**: `text-embedding-3-large`
    - **Deployment type**: Standard
    - **Model version**: *Selecciona la versión predeterminada*
    - **Recurso de OpenAI**: *Selecciona el recurso creado previamente*
    - **Tokens per Minute Rate Limit (thousands)**: 150K
    - **Content filter**: DefaultV2
    - **Enable dynamic quota**: Disabled

    > Nota: Si la ubicación de tu recurso actual no tiene cuota disponible para el modelo que deseas desplegar, se te solicitará elegir una ubicación diferente donde se creará un nuevo recurso y se conectará a tu proyecto.

4. Repite los pasos anteriores para desplegar un modelo **gpt-4o-2024-11-20** con el nombre de despliegue `gpt-4o`.

    > Nota: Reducir los tokens por minuto (TPM) ayuda a evitar el sobreuso de la cuota disponible en tu suscripción. 150.000 TPM es suficiente para los datos utilizados en este ejercicio.

## Crear um almacenamento para nuestros datos

### 1. Acceder al portal de Azure
- Ve a https://portal.azure.com e inicia sesión con tus credenciales.

### 2. Crear una nueva cuenta de almacenamiento
- Haz clic en "Crear un recurso".
- Selecciona "Almacenamiento" y luego "Storage accounts".
- Presiona el boton crear

  - **Subscription**: *Selecciona tu suscripción de Azure*
    - **Resource group**: *Selecciona o crea un grupo de recursos*
    - **Storage account name**: *Ingresa un nombre de servicio único*
    - **Location**: *Haz una elección **aleatoria** entre alguna de las siguientes regiones*\*
        - Australia East
        - Canada East
        - East US
        - East US 2
        - France Central
        - Japan East
        - North Central US
        - Sweden Central
        - Switzerland 
    - **Primary service**: Azure Blob Storage

- Dentro del recurso de Almacenamiento, crear un Container llamado `data`
    - Data Storage -> Containers -> + Container


## Crear un índice para tus datos

Ahora vamos a crear un índice en tu recurso de Azure AI Search.

- Seleccione **Import and Vectorize data**

- Conectarse a los datos
 ![Captura de pantalla del Wizard de Search](./media/azure-search-step-1.png)

- Vectorizar 
 ![Captura de pantalla del Wizard de Search](./media/azure-search-step-2.png)

- Revisar y Crear
 ![Captura de pantalla del Wizard de Search](./media/azure-search-step-3.png)


## Probar el índice

Antes de utilizar tu índice en un flujo de solicitud basado en RAG, verifiquemos que se puede usar para generar respuestas de IA generativa.

1. En el panel de navegación a la izquierda, selecciona la página **Playgrounds**.
1. En la página de Chat, en el panel de Configuración, asegúrate de que esté seleccionado el despliegue del modelo **gpt-35-turbo-16k**. Luego, en el panel principal de la sesión de chat, envía la solicitud `Where can I stay in New York?`
1. Revisa la respuesta, que debería ser una respuesta genérica del modelo sin datos del índice.
1. En el panel de Configuración, expande el campo **Agregar tus datos**, y luego agrega el índice del proyecto **brochures-index** y selecciona el tipo de búsqueda **hybrid (vector + keyword)**.

   > **Nota**: Algunos usuarios están encontrando que los índices recién creados no están disponibles de inmediato. Actualizar el navegador generalmente ayuda, pero si aún experimentas el problema de que no se encuentra el índice, puede que necesites esperar hasta que el índice sea reconocido.

1. Después de que el índice se haya agregado y la sesión de chat se reinicie, vuelve a enviar la solicitud `Where can I stay in New York?`
1. Revisa la respuesta, que debería basarse en los datos del índice.

## Usar el índice en un flujo de solicitudes

Tu índice vectorial se ha guardado en tu proyecto de Azure AI Foundry, lo que te permite utilizarlo fácilmente en un flujo de solicitudes.

1. En el portal Azure AI Foundry, en tu proyecto, en el panel de navegación a la izquierda, bajo **Build and customize**, selecciona la página **Prompt flow**.
1. Crea un nuevo flujo de solicitudes clonando la muestra **Multi-Round Q&A on Your Data** de la galería. Guarda tu clon de esta muestra en una carpeta llamada `brochure-flow`.
    <details>  
      <summary><b>Consejo para solución de problemas</b>: Error de permisos</summary>
        <p>Si recibes un error de permisos al crear un nuevo flujo de solicitudes, intenta lo siguiente para solucionarlo:</p>
        <ul>
          <li>En el portal de Azure, selecciona el recurso de AI Services.</li>
          <li>Bajo Resource Management, en la pestaña Identity, confirma que tiene asignada la identidad administrada del sistema.</li>
          <li>Navega a la Storage Account asociada. En la página de IAM, añade la asignación de rol <em>Storage blob data reader</em>.</li>
          <li>Bajo <strong>Assign access to</strong>, elige <strong>Managed Identity</strong>, <strong>+ Select members</strong>, selecciona las <strong>All system-assigned managed identities</strong> y selecciona tu recurso de Azure AI Services.</li>
          <li>Revisa y asigna para guardar la nueva configuración y reintenta el paso anterior.</li>
        </ul>
    </details>

1. Cuando se abra la página del diseñador de flujos de solicitud, revisa **brochure-flow**. Su diagrama debería parecerse a la siguiente imagen:

    ![Una captura de pantalla de un diagrama de flujo de chat](./media/chat-flow.png)

    La muestra de flujo de solicitud que estás utilizando implementa la lógica para una aplicación de chat en la que el usuario puede enviar de forma iterativa entradas de texto. El historial conversacional se retiene y se incluye en el contexto para cada iteración. El flujo de solicitud orquesta una secuencia de *herramientas* para:

    - Añadir el historial a la entrada de chat para definir una solicitud en forma de pregunta contextualizada.
    - Recuperar el contexto utilizando tu índice y un tipo de consulta de tu elección basado en la pregunta.
    - Generar un contexto de solicitud utilizando los datos recuperados del índice para complementar la pregunta.
    - Crear variantes de la solicitud añadiendo un mensaje del sistema y estructurando el historial de chat.
    - Enviar la solicitud a un modelo de lenguaje para generar una respuesta en lenguaje natural.

1. Usa el botón **Start compute session** para iniciar el cómputo en tiempo real para el flujo.

    Espera a que se inicie la sesión de cómputo. Esto proporciona un contexto de cómputo para el flujo de solicitudes. Mientras esperas, revisa en la pestaña **Flow** las secciones correspondientes a las herramientas del flujo.

1. En la sección **Inputs**, asegúrate de que las entradas incluyan:
    - **chat_history**
    - **chat_input**

    El historial de chat predeterminado en esta muestra incluye algunas conversaciones sobre IA.

1. En la sección **Outputs**, asegúrate de que la salida incluya:

    - **chat_output** con el valor ${chat_with_context.output}

1. En la sección **modify_query_with_history**, selecciona la siguiente configuración (dejando las demás como están):

    - **Connection**: *El recurso de Azure OpenAI predeterminado para tu AI hub*
    - **Api**: chat
    - **deployment_name**: gpt-35-turbo-16k
    - **response_format**: {"type":"text"}

1. Espera a que la sesión de cómputo se inicie, luego en la sección **lookup**, establece los siguientes valores de parámetros:

    - **mlindex_content**: *Selecciona el campo vacío para abrir el panel Generate*
        - **index_type**: Registered Index
        - **mlindex_asset_id**: brochures-index:1
    - **queries**: ${modify_query_with_history.output}
    - **query_type**: Hybrid (vector + keyword)
    - **top_k**: 2

1. En la sección **generate_prompt_context**, revisa el script de Python y asegúrate de que las **inputs** para esta herramienta incluyan el siguiente parámetro:

    - **search_result** *(object)*: ${lookup.output}

1. En la sección **Prompt_variants**, revisa el script de Python y asegúrate de que las **inputs** para esta herramienta incluyan los siguientes parámetros:

    - **contexts** *(string)*: ${generate_prompt_context.output}
    - **chat_history** *(string)*: ${inputs.chat_history}
    - **chat_input** *(string)*: ${inputs.chat_input}

1. En la sección **chat_with_context**, selecciona la siguiente configuración (dejando las demás como están):

    - **Connection**: Default_AzureOpenAI
    - **Api**: Chat
    - **deployment_name**: gpt-35-turbo-16k
    - **response_format**: {"type":"text"}

    Luego, asegúrate de que las **inputs** para esta herramienta incluyan los siguientes parámetros:
    - **prompt_text** *(string)*: ${Prompt_variants.output}

1. En la barra de herramientas, usa el botón **Save** para guardar los cambios realizados en las herramientas del flujo de solicitudes.
1. En la barra de herramientas, selecciona **Chat**. Se abrirá un panel de chat con el historial de conversación de la muestra y la entrada completada automáticamente basada en los valores de ejemplo. Puedes ignorar estos valores.
1. En el panel de chat, reemplaza la entrada predeterminada con la pregunta `Where can I stay in London?` y envíala.
1. Revisa la respuesta, la cual debería basarse en los datos del índice.
1. Revisa las salidas de cada herramienta en el flujo.
1. En el panel de chat, ingresa la pregunta `What can I do there?`
1. Revisa la respuesta, que debería basarse en los datos del índice y tener en cuenta el historial de chat (de modo que "there" se entienda como "en Londres").
1. Revisa las salidas de cada herramienta en el flujo, notando cómo cada herramienta operó sobre sus entradas para preparar una solicitud contextualizada y obtener una respuesta apropiada.

## Desplegar el flujo

Ahora que tienes un flujo funcional que utiliza tus datos indexados, puedes desplegarlo como un servicio para ser consumido por una aplicación copiloto.

> **Nota**: Dependiendo de la región y la carga del centro de datos, los despliegues a veces pueden tardar un tiempo y en ocasiones pueden arrojar un error al interactuar con el despliegue. Si lo deseas, puedes continuar con la sección de desafíos mientras se despliega o saltarte la prueba de tu despliegue si tienes poco tiempo.

1. En la barra de herramientas, selecciona **Deploy**.
1. Crea un despliegue con la siguiente configuración:
    - **Basic settings**:
        - **Endpoint**: New
        - **Endpoint name**: *Usa el nombre de endpoint único predeterminado*
        - **Deployment name**: *Usa el nombre de despliegue predeterminado*
        - **Virtual machine**: Standard_DS3_v2
        - **Instance count**: 3
        - **Inferencing data collection**: Seleccionado
    - **Advanced settings**:
        - *Usa la configuración predeterminada*
1. En el portal Azure AI Foundry, en tu proyecto, en el panel de navegación a la izquierda, bajo **My assets**, selecciona la página **Models + endpoints**.
1. Sigue actualizando la vista hasta que el despliegue **brochure-endpoint-1** se muestre como *succeeded* bajo el endpoint **brochure-endpoint** (esto puede tomar un período de tiempo considerable).
1. Cuando el despliegue haya sido exitoso, selecciónalo. Luego, en su página **Test**, ingresa la solicitud `What is there to do in San Francisco?` y revisa la respuesta.
1. Ingresa la solicitud `Where else could I go?` y revisa la respuesta.
1. Visualiza la página **Consume** del endpoint y observa que contiene la información de conexión y código de ejemplo que puedes utilizar para construir una aplicación cliente para tu endpoint, permitiéndote integrar la solución del flujo de solicitudes en una aplicación como un copiloto personalizado.

## Desafío 

¡Ahora has experimentado cómo integrar tus propios datos en una aplicación de IA generativa construida con el portal Azure AI Foundry, vamos a profundizar aún más!

Intenta agregar una nueva fuente de datos a través del portal Azure AI Foundry, indexarla e integrarla en un flujo de solicitudes. Algunos conjuntos de datos que podrías probar son:

- Una colección de artículos (de investigación) que tengas en tu computadora.
- Un conjunto de presentaciones de conferencias pasadas.
- Cualquiera de los conjuntos de datos disponibles en el repositorio de [Azure Search sample data](https://github.com/Azure-Samples/azure-search-sample-data).

¡Sé lo más ingenioso posible para crear tu propia fuente de datos e integrarla en tu flujo de solicitudes! Prueba el nuevo flujo de solicitudes y envía preguntas que solo puedan ser respondidas usando el conjunto de datos que hayas elegido.

## Limpieza

Para evitar costos y utilización innecesaria de recursos en Azure, deberías eliminar los recursos desplegados en este ejercicio.

1. Si ya has finalizado la exploración de Azure AI Foundry, regresa al [portal de Azure](https://portal.azure.com) en `https://portal.azure.com` e inicia sesión con tus credenciales de Azure si es necesario. Luego, elimina los recursos en el grupo de recursos donde se aprovisionaron tu recurso de Azure AI Search y los recursos de Azure AI.