# Como crear un archivo de esquemas para crear tablas con DynamoDB

## Trabajando con Tablas

Si vemos la documentación de la API de _boto3_ podemos ver que al cliente podemos pasarle múltiples argumentos:

```python
import boto3

client = boto3.client('dynamodb')
response = client.create_table(
    AttributeDefinitions=[
        {
            'AttributeName': 'string',
            'AttributeType': 'S'|'N'|'B'
        },
    ],
    TableName='string',
    KeySchema=[
        {
            'AttributeName': 'string',
            'KeyType': 'HASH'|'RANGE'
        },
    ],
    LocalSecondaryIndexes=[
        {
            'IndexName': 'string',
            'KeySchema': [
                {
                    'AttributeName': 'string',
                    'KeyType': 'HASH'|'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL'|'KEYS_ONLY'|'INCLUDE',
                'NonKeyAttributes': [
                    'string',
                ]
            }
        },
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'string',
            'KeySchema': [
                {
                    'AttributeName': 'string',
                    'KeyType': 'HASH'|'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL'|'KEYS_ONLY'|'INCLUDE',
                'NonKeyAttributes': [
                    'string',
                ]
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 123,
                'WriteCapacityUnits': 123
            }
        },
    ],
    BillingMode='PROVISIONED'|'PAY_PER_REQUEST',
    ProvisionedThroughput={
        'ReadCapacityUnits': 123,
        'WriteCapacityUnits': 123
    },
    StreamSpecification={
        'StreamEnabled': True|False,
        'StreamViewType': 'NEW_IMAGE'|'OLD_IMAGE'|'NEW_AND_OLD_IMAGES'|'KEYS_ONLY'
    },
    SSESpecification={
        'Enabled': True|False,
        'SSEType': 'AES256'|'KMS',
        'KMSMasterKeyId': 'string'
    },
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ],
    TableClass='STANDARD'|'STANDARD_INFREQUENT_ACCESS'
)
```
_
Veamos en detalles que significan estas cosas, en particular nos van a interesar _TableName_, _KeySchema_, _AttributeDefinitions_, y 
eventualmente los índices:

- ```TableName```: Esto corresponde al nombre de la tabla con el que va a figurar en _DynamoDB_, recordemos que aqui podemos usar alfanumérico
pero AWS no recomienda usar '_' dentro del nombre. _CamelCase_ puede ser una buena opción.
- ```KeySchema```: Esta esa la definición de las keys que vamos a usar, por ello tenemos que definir al menos una clave tipo _HASH_ que equivale
a lo que definimos como _PartitionKey_ y opcionalmente podemos proveer una _RANGE_ key que corresponde a la _SortKey_. Notamos aca que el 
diccionario contiene únicamente el tipo de key y los nombres de las mismas.
    ```
    "KeySchema": [
        {
            "AttributeName": "MyPartitionKey",
            "KeyType": "HASH"
        },
        {
            "AttributeName": "MySortKey",
            "KeyType": "RANGE"
        }
    ]
    ```
- ```AttributeDefinitions```: Aquí vamos a definir la información correspondiente a los tipos de datos de las keys definidas en _KeySchema_.
Los tipos de datos soportado en _AttributeType_ son ***S*** (_String_), ***N*** (_Numeric_) y ***B*** (_Binary_)
    ```
    "AttributeDefinitions": [
        {
            "AttributeName": "MyPartitionKey",
            "AttributeType": "N"
        },
        {
            "AttributeName": "MySortKey",
            "AttributeType": "S"
        }
    ]
    ```

## Trabajando con items

De igual manera trabajando con tablas, tenemos la misma definición cuando queremos insertar un item, dentro de su documentación
podemos ver que los parámetros varian considerablemente a la hora de insertar un item:

```python
import boto3

client = boto3.client('dynamodb')
response = table.put_item(
    Item={
        'string': 'string'|123|Binary(b'bytes')|True|None|set(['string'])|set([123])|set([Binary(b'bytes')])|[]|{}
    },
    Expected={
        'string': {
            'Value': 'string'|123|Binary(b'bytes')|True|None|set(['string'])|set([123])|set([Binary(b'bytes')])|[]|{},
            'Exists': True|False,
            'ComparisonOperator': 'EQ'|'NE'|'IN'|'LE'|'LT'|'GE'|'GT'|'BETWEEN'|'NOT_NULL'|'NULL'|'CONTAINS'|'NOT_CONTAINS'|'BEGINS_WITH',
            'AttributeValueList': [
                'string'|123|Binary(b'bytes')|True|None|set(['string'])|set([123])|set([Binary(b'bytes')])|[]|{},
            ]
        }
    },
    ReturnValues='NONE'|'ALL_OLD'|'UPDATED_OLD'|'ALL_NEW'|'UPDATED_NEW',
    ReturnConsumedCapacity='INDEXES'|'TOTAL'|'NONE',
    ReturnItemCollectionMetrics='SIZE'|'NONE',
    ConditionalOperator='AND'|'OR',
    ConditionExpression=Attr('myattribute').eq('myvalue'),
    ExpressionAttributeNames={
        'string': 'string'
    },
    ExpressionAttributeValues={
        'string': 'string'|123|Binary(b'bytes')|True|None|set(['string'])|set([123])|set([Binary(b'bytes')])|[]|{}
    }
)
```

En nuestro caso nos concentraremos en el parámetro _Item_, este es un diccionario que puede contener toda la información de los 
atributos que queremos guardar:

```
Item = {
    "MyPartitionKey": {"N": "101"},
    "MySortKey": {"S": "AGoodSortableHash"},
    "MyListAttribute": { "L": [
        {
            "S": "SomeValue"
        },
        {
            "S": "SomeOtherValue"
        }
    ]},
    "MyMapAttribute": { "M": {
            "SomeKeyInMyMap":{
                "S": "OtherValue"
            },
            "SomeListInTheMap":{ "L": [
                    {
                        "S": "MoreValues"
                    }
                ]
            }
        }
    }
}
```

Aquí tenemos varios tipos de datos en juego y podemos ver como esto varía y se puede generar dinámicamente. Por esto es recomendable utilizar
el recurso (resource) de _boto3_ para que haga las interpretaciones necesarias para convertir de manera correcta nuestros datos y los datos
de _DynamoDB_.

