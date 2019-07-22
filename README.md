# lambdapool

## Overview

Lambda Pool is a tool through which a developer can deploy code on AWS Lambda and call the same code easily with a simple and comprehendible interface without going too much out of way from existing code.

The other primary objective is to abstract away the process of creating a Lambda function which is also tedious and requires domain knowledge. The goal of this tool is to remove the requirement of domain knowledge when trying to use serverless technology in day to day developer workflow.

## Features

- CLI to create, list, update and delete functions
- Support for specifying function layers, list layers used foreach functions
- LambdaPool interface
- LambdaExecutor Interface

## Installation

`lambdapool` can be installed by installing the tarball from [here](https://lambdapool-releases.s3.amazonaws.com/lambdapool-0.9.7.tar.gz)

```bash
$ pip install --user https://lambdapool-releases.s3.amazonaws.com/lambdapool-0.9.7.tar.gz
Collecting https://lambdapool-releases.s3.amazonaws.com/lambdapool-0.9.7.tar.gz
  Downloading https://lambdapool-releases.s3.amazonaws.com/lambdapool-0.9.7.tar.gz
...
Installing collected packages: lambdapool
Successfully installed lambdapool-0.9.7
```

Currently, the package is being released as a tarball. Plans are underway to distribute `lambdapool` through PyPI.

## Genesis

The `algoshelf` stack of software needs a Task Queue to run data pipelines like forecast computation. The constituent tasks can be broken down into independent components which can be parallely scheduled. One way of doing this running the tasks on different machine cores using `multiprocessing`. But, this is not very scalable and leads to wastage of compute resources as the resources lie idle for most periods of time.

A better way to tackle the problem is to use serverless technology as a backend for running the computation. There are various serverless options in market pushed by the major cloud providers, for example, Amazon Web Services Lambda by Amazon and Google Cloud functions by Google. Serverless abstracts away the underlying compute resources. The users don't need to think about spawning infrastructure, scaling them up during high resource usage and scaling them back down when idle. The idea is to make running the compute workloads `virtually infinitely scalable` (subject to AWS limitations).

## Usage - Command Line Interface

`lambdapool` ships with a CLI to manage the code uploaded to AWS Lambda. The tool allows you to create, delete, list and update Lambda functions.

```bash
$ lambdapool
Usage: lambdapool [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create  Create a new function
  delete  Delete a function
  list    List all deployed functions
  update  Update an existing function
```

More information can be found regarding each of the above commands by `lambdapool <command> --help`

```bash
$ lambdapool create --help
Usage: lambdapool create [OPTIONS] FUNCTION_NAME [PATHS]...

  Create a new function

Options:
  -r, --requirements PATH  Specifies the dependencies to be installed along
                           with the function
  --memory INTEGER         Sets the memory size of the function environment
  --timeout INTEGER        Sets the timeout for the function in seconds
  --layers TEXT            Sets the layers to be used when the function is
                           ran. The Layers ARN's (a maximum of 5) should be
                           specified.
  --help                   Show this message and exit.
```

### Creating a lambda function

Any python module can be deployed to Lambda using the `create` command.

For example, let's take the below code:

```bash
examples $ tree algorithms/
algorithms
├── algorithms.py
└── __init__.py

examples $ cat algorithms/algorithms.py
def fibonacci(n):
    '''A naive implementation of computing n'th fibonacci number
    '''
    if n==0: return 0
    if n==1: return 1
    return fibonacci(n-1) + fibonacci(n-2)
```

The above can be deployed to lambda using:

```bash
$ cd examples/
examples $ lambdapool create algorithms algorithms/ --timeout=300 --memory=128
=== Creating lambdapool function ===
=== Copying all specified files and directories ===
Copying algorithms.py...
...
=== Succesfully created lambdapool function algorithms ===
```

The specified code is now uploaded to AWS Lambda as a Lambda function. This is now ready to be consumed in your code. The API for LambdaPool is explained below.

### Listing all lambda functions

The Lambda functions created by `lambdapool` can be listed down by the `list` subcommand.

```bash
examples $ lambdapool list
FUNCTION NAME    SIZE      WHEN              RUNTIME MEMORY (MB)    TIMEOUT (SEC)
---------------  --------  --------------  ---------------------  ---------------
algorithms       49.75 KB  20 seconds ago                    128              300
```

### Deleting a lambda function

The Lambda functions can be deleted by `delete` subcommand. You need to specify the name of the lambda function created.

```bash
examples $ lambdapool delete algorithms
=== Deleting lambdapool function ===
=== Deleted lambdapool function algorithms===
```

### Updating a lambda function

After deploying your code, you might want to make changes to it. After making the relevant changes, the code can be redeployed to Lambda using the `update` subcommand.

Let's add a `factorial` function to `algorithms/algorithms.py`.

```python
# algorithms/algorithms.py

def fibonacci(n):
    '''A naive implementation of computing n'th fibonacci number
    '''
    if n==0: return 0
    if n==1: return 1
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    '''Returns factorial of a number
    '''
    if n<0: raise ValueError('Factorial of a negative number does not exist')
    if n==0: return 1
    return n*factorial(n-1)
```

```bash
examples $ lambdapool update algorithms algorithms --memory 128 --timeout 300
=== Updating lambdapool function ===
== Copying all specified files and directories ===
Copying algorithms...
=== Copied all specified files and directories ===
...
=== Uploading function and dependencies ===
=== Function algorithms uploaded along with all dependencies ===
=== Updated lambdapool function algorithms ===
```

## LambdaPool API

The user should be able to create a pool of workers, specifying the maximum concurrency. Also, LambdaPool would require the name of the Lambda function that sits as an entrypoint on AWS Lambda.

```python
>>> from lambdapool import LambdaPool
>>> pool = LambdaPool(
    workers=10,
    lambda_function='algorithms',
    aws_access_key_id='...',
    aws_secret_access_key='...',
    aws_region_name='...'
    )
```

> If the AWS credentials are not provided, system defaults are used.

The user can perform a single synchronous task like the following:

```python
>>> from algorithms.algorithms import fibonacci
>>> pool.apply(fibonacci, args=[10])
55
```

Or, you can specify keyword arguments instead also,

```python
>>> pool.apply(fibonacci, kwds={'n': 10})
55
```

An asynchronous invocation is possible as:

```python
>>> result = pool.apply_async(fibonacci, kwds={'n': 10})
>>> result
<class 'multiprocessing.pool.ApplyResult'>
>>> result.get()
55
```

The user can also use map to perform mutliple tasks at the same time.

```python
>>> pool.map(fibonacci, range(100))
[0, 1, 1, 2, 3, 5, 8, ...]
```

> Note: The `LambdaPool.map` interface does not support keyword arguments. Passing more than one argument is also not possible. This is a decision strictly taken to conform with `multiprocessing.pool.ThreadPool` [API](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool).


## LambdaExecutor API

Python 3.5 introduced a new interface to perform concurrent computing. This was named the `Executor` [API](https://docs.python.org/3/library/concurrent.futures.html#executor-objects). Concurrent workloads can be run on threads using `ThreadPoolExecutor` and on seperate processess using `ProcessPoolExecutor`.

LambdaPool also exposes a similar interface known as `LambdaExecutor`. It has the exact similar functions and function signatures to run python callables asynchronously. The initializer is a bit different.

```python
>>> from lambdapool import LambdaExecutor
>>> from algorithms.algorithms import fibonacci
>>> with LambdaExecutor(lambda_function='algorithms') as executor:
...    futures = [executor.submit(fibonacci, n) for n in range(100)]
...    fibonaccis = [f.result() for f in futures]

>>> fibonaccis
[0, 1, 1, 2, 3, 5, 8, ...]

```

The `submit` method returns what is known as a [Future](https://docs.python.org/3/library/concurrent.futures.html#future-objects) object. This follows the Python native way of handling the encapsulated data. `LambdaExecutor` is just a wrapper on top of the `ThreadPoolExecutor` interface providing the added features of invoking the functions on the AWS Lambda infrastructure and not on the client computer. This way very high levels of concurrency can be achieved.

> Note: The above example assumes that the functions are already deployed to Lambda, as shown [here](#deployment)

## Limitations

- Serialization of the payload is being a hurdle. Need to find better solutions than Cloudpickle.
- The decoupling between function provisioning and execution can cause incoherencies.

## Future Work

- Permissions management system
- System to fetch execution logs
- Extend the system to GCF

## Contributing

We welcome contributions from the community. The guidelines can be found [here](CONTRIBUTING.md)

## License

`lambdapool` is covered under the [Apache 2.0 License][license]

## Code of Conduct

All maintainers, contributors and people involved with the project are bound by the [Code of Conduct][coc]

## Contact

- [Rorodata Public Slack][slack]
- [team@rorodata.com][rorodata-team]


[coc]: CODE_OF_CONDUCT.md
[slack]: https://slack.rorocloud.io
[changelog]: CHANGELOG.md
[license]: LICENSE
[rorodata-team]: mailto:team@rorodata.com
