

## Data Engineering Challenge- Doodle
The challenge represents a problem where we have to create an application that processes a data stream.

I have used Python as my language of choice as I have not used JAVA in some time and therefore am more comfortable in Python.
####
The main libraries used in the code are mentioned below. The rest are mentioned in this requirement file.

 - kafka-python
 - hyperloglog
 - memory-profiler
 - time

## Steps

### Step 1: Installation and Setup

 - Installed Kafka using [this](https://kafka.apache.org/quickstart) great introductory tutorial. 
  - Installed python-kafka using this pip.

    

> pip install kafka-python

### Step 2: Topic creation and data input
Download the [data file](https://tda-public.s3.eu-central-1.amazonaws.com/hire-challenge/stream.jsonl.gz) and upload it into a topic using the command below.

    

> gzip -dc stream.jsonl.gz | kafka_2.13-3.1.0/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic doodle_data

### Step3: Processing
Then I created a consumer to pull the frames from the topic. **I wanted to parse JSON once** and use that to calculate unique users per `duration`. The `duration` is a range of time and is configurable. I used a time rounding function that rounds the time to the next mentioned `duration`. For example, if `duration` is 1 hour, then all the timestamps between two hours are rounded to the later hour. With this functionality, I have implemented two counting strategies.

 - Users per minute  
 - Users per 10 minutes

But we can easily change the `duration` of counting with a change in only one variable and calculate users per `duration` by parsing the JSON only once in the same run.

### Step 4: Count the unique `UID`s
I created 2 different approaches to count the unique `UID`s.

 - **Naive approach**: Created a list that stores all the `UID`s in a
   `duration`. Then put the data in a `set` to obtain unique users.
 -  **HyperLogLog** (`HLL`): I realized that memory requirement to store `UID`s for a longer duration would require a lot of memory. Therefore, I used the `HLL` algorithm to keep the application's memory footprint as low as possible. Memory is not an issue for small durations but will take huge dumps of memory if the `duration` is 24 hours.
 
Some benchmarks can be seen below. We can see that the memory required to complete the counting of users per minute and 10 minutes(both calculated in the same run) is less in the case of HLL with almost the same amount of time. So the HLL algorithm takes 40% less memory than the naive approach.
```
----------List processing-------
 Maximum memory usage: 91.98046875
Time taken by list DS 73.11751055717468
----------HLL algorithm-------
Maximum memory usage: 55.58984375
Time taken by list HLL 74.02316451072693
```
I have also implemented a performance measurement that measures the time to process `n` messages and write the processing time to a text file (implemented with `n`=50000). We can use a watcher over this file and create a dashboard that shows the time to process `n` messages. The value of `n` is configurable, and this will help to monitor a problem if the time to process `n` events exceeds that of average time. The output to a text file can be replaced with output to a database or maybe even a topic in Kafka.

### Step 5: Output
The results are pushed to a new topic in Kafka called `metrics` in the JSON format. The following JSON format was used to put the results into the topic.
```
{  
  "duration": duration,  # can be any duration. I used "minute" and "10 minutes"
  "Start_time": startTime,  # the starting time of counting
  "End_time": endTime,  #the ending time of counting
  "Metric": {  
        "total_UIDs": totalUIDs,  # total UIDs
		"unique_UIDs": uniqueUIDs  # unique UIDs
			}  
}
```

### Memory profiler
The application uses memory-profiler library to check the memory used by the functions. I used the maximum memory that was consumed during the complete run of a function for evaluation.

### Scaling 
We can create a consumer group that takes input from different partitions for creating the performance measure. Then process it in SPARK to get the advantage of parallel in-memory processing.

- If a topic has `n` partitions, we can create a consumer group with `n` consumers for each partition.
 -  Then, we can use `n` nodes in a Spark cluster to process the data and obtain the performance metrics.

### Coping with failure
Kafka persists the state of processed frames (messages) using the offset. In case of a failure, the application can restart using the offset. But the data that is in memory will be lost. We can create a failure coping mechanism that can look at the past data and interpolate the missing data. (Assumption: data follows a trend: daily, monthly or even yearly)

### Late or random timestamp
If the timestamp is late, then it will be added to the next window. We can also create a `map` to store the data. Instead of pushing the metrics into a topic as soon as it is done, we can wait for some time and add the late timestamp into the `map`.

We can devise a strategy to drop it `50%` of the times for random timestamp and keep it `50%` of the times. The probability of `50%` can be changed according to the probability of how often we receive a random timestamp.

### JSON parser impact on performance
JSON is popular because it is human-readable, relatively concise, simple to understand, and is universally supported. But it takes a lot of space. Other formats like **Avro** can be suitable for messages, but it has an overhead of creating a schema registry. We can also use **MessagePack**  as it has a native implementation in Kafka and can be used just like JSON.
