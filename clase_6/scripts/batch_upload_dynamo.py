import boto3
import glob
import json

def create_table(table_name: str,
                 schema: list,
                 ddb_resource: boto3.resource = None) -> None:
    ## Primero vamos a validar que el recurso existe, si no se crea uno
    
    if ddb_resource is None:
        ddb_resource = boto3.resource('dynamodb')
    print('create_table:: Creando Tabla...')
    try:
        # Create the DynamoDB table.
        table = ddb_resource.create_table(
            TableName = table_name, ## Nombre de la tabla a crear
            ## Aqui definimos las formas de tablas a crear, si ven el json
            ## podemos ver que los tipos de key son HASH y RANGE, estas corresponde
            ## a Partiton Key y Sorted Key respectivamente
            KeySchema = schema.get('KeySchema'),
            ## Aqui definimos el tipo de datos de las Keys que recordemos que 
            ## estos se tienen que definir a la hora de la creacion de la tabla
            ## y no se pueden cambiar on the fly
            AttributeDefinitions = schema.get('AttributeDefinitions'),
            ProvisionedThroughput = {
                ## Vamos a dejar la configuracion por defecto
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        assert table.item_count == 0
    except:
        raise
     
    print('create_table:: Tabla creada...')

if __name__ == '__main__':
    
    ## Creamos un recurso (conexion) contra dynamodb
    ## vale la pena notar que si no seteamos credenciales, el script
    ## va a tomar las credenciales que tengan configuradas mediante aws cli
    ## por defecto estas estan en la carpeta ~/.aws/
    dynamodb = boto3.resource('dynamodb')
    
    ## Primero validamos las tablas que estan creadas en nuestro entorno
    table_iterator = dynamodb.tables.all()
    print('Tablas actualmente creadas en el entorno:')
    for table in table_iterator:
        print(f'\t-- {table.name}')
    
    ## Listamos los archivos que queremos levantar (pueden copiar el ejemplo
    ## de JSON que comienza con boto3 y crear los suyos dejando boto3 como primera
    ## parte del nombre)
    file_list = glob.glob('dynamodb_data/boto3*.json')
    print('Tablas leidas por crear:')
    for file in file_list:
        print(f'\t-- {file}')
        
    ## Validamos si la tabla a crear existe, si no existe la vamos a crear
    
    for file in file_list:
        with open(file) as fd:
            data = json.load(fd)

            table_name = data.get('table_name')
            table_schema = data.get('schema')
            table_items = data.get('items')
            
            if table_name not in [t.name for t in table_iterator]:
                create_table(table_name, table_schema, dynamodb)
            ## Validamos que la tabla se cree correctamente
            try:
                assert table_name in [t.name for t in dynamodb.tables.all()]
                print(f'La tabla {table_name} se creo correctamente')
            except AssertionError:
                print('Se produjo un error al crear la tabla')

            ## Finalmente vamos a cargar los datos, en el caso de querer utilizar
            ## los JSON de Forum, ProductCatalog, etc, se deberia hacer un caso
            ## adicional donde leemos el campo Table[item][Method] y si es PutRequest
            ## utilizamos DynamoDB.Table.put_item() por ejemplo
            
            ## Inicializamos la tabla a popular (el objeto de dynamo, simil a el
            ## "cursor" en RBD's o todo SDK que es valido con PEP-249)
            ## https://peps.python.org/pep-0249/
            
            table_to_use = dynamodb.Table(table_name)
            ## Aqui vamos a usar batch_writer para informarle de antemano
            ## a AWS que vamos a hacer multiples request de PUT para no 
            ## incursionar en exceso de pedidos.
            with table_to_use.batch_writer() as batch:
                for item in table_items:
                    ## Escribimos el dato
                    batch.put_item(
                        Item = item
                    )
                
            ## Ahora validamos que los datos persistan en la tabla!
            
            results = table_to_use.scan()
            
            for response in results['Items']:
                print(f'Objetos encontrados por la query: {response}')
                
                