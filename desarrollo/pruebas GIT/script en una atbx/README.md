Estas herramientas fueron creadas en el trabajo para extraer a capa KML todos los registros de una capa mediante un atributo que los identifica.
El caso concreto es:
	Obtener las KML de cada país a partir de una sola capa con todos los países

Par poder compartirla y que funcione, seguí estos pasos
En en ArcGIS Pro de origen (trabajo) abrí los scripts 
	AddMessage.py
	Feature To Kml.py
y los exporté a un archivo de localización controlada, llevandomelos así.

Luego, cree una nueva toolbox. Abrí el modelo en la toolbox original del proyecto de origen del trabajo. Para guardarlo, usé la opción guardar como (pestaña ModelBuilder en AGP)
Luego lo exporté a la nueva toolbox y me la llevé junto a los archivos de python.

PONERLA A FUNCIONAR EN EL NUEVO ENTORNO

puse los scripts y la toolbox en un entorno controlado.
Cree un nuevo proyecto donde iban a ser usados
moví ahí el archivo atbx (sólo)
en el proyecto, añadí una nueva toolbox, selecionando esta.

Los scripts no he encontrado forma de agregarlos a la toolbox, por los que tuve que volver a crearlos (ver fotos para la configuración)

El modelo si que se abrió. No funciona porque la referencia al script de AddMessage no funciona adecuadamente, por lo que deben retirarse los mensajes y volverlos a crear (el contenido de los mensajes está en las imágenes también