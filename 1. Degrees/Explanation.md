# Introduction
The purpose of this exercise was to find connections between Hollywood actors 
and actresses. 

We had a large dataset of:
- **Stars:** a list of actors and actresses
- **Movies:** details about movies
- **Casting:** which actor/actress starred in which movie

Also the path that we found had to be the shortest.

# Overview of the Code

The approach to solving this problem was inspired by treating 
everything as a **data structure**. I envisioned the entire 
exercise as navigating a **graph** or a maze.

To break it down further:
- **Stars as Nodes:** Each actor or actress is represented as a node in the graph.
- **Movies as Edges:** Each movie acts as an edge connecting the stars.
  
By representing the data this way, I could leverage the 
**Breadth-First Search (BFS)** algorithm to:
- Traverse the graph step by step in all directions.
- Stop the search as soon as the target actor is found.
- Return the connection path between the two actors.

# Detailed Code Explanation

## Input / Output

The function `shortest_path` takes two parameters: **source** and **target**.

```python
def shortest_path(source, target)
```

- **source:** The unique identifier (ID) of the source actor.
- **target:** The unique identifier (ID) of the target actor.

### Output

The function returns a list of tuples, where each tuple represents a step in 
the connection path between the source and target actors. Each tuple is formatted as:

```
(movie_id, actor_id)
```

Each tuple shows one connection step, starting from the source actor and 
progressively moving closer to the target actor.

#### Example Output

For instance, the function might return:

```python
[('112384', '158'), ('109830', '705'), ('93779', '1697')]
```

This output indicates that the source actor is connected to another 
actor via movie `112384`, then that actor is connected via movie `109830`,
and finally, the target actor is reached via movie `93779`.

## Core logic
Now the core logic goes like this. First we initialize all the necessary variables and data structures
which include an actual target node which initially is None. Queue for storing nodes which we
should visit next. And the visited nodes so that we don't accidentally visit already visited nodes.
```python
queue = QueueFrontier()
visited = []

neighbors = neighbors_for_person(source)
visited.append(source)

target_node = None
```

Next, we handle the initial exploration of neighboring nodes. This step is crucial 
for pre-populating the queue before we enter the main loop (which will be explained 
later). Since the `neighbors_for_person(source)` method is already defined, 
we simply retrieve the neighbors and process each one. For every neighbor, we 
create a new `Node` object and add it to the queue.

```python
for neighbor in neighbors:
    if neighbor not in visited:
        movie_id = neighbor[0]
        person_id = neighbor[1]

        neighbor_node = Node(person_id, None, movie_id)

        if person_id == target:
            target_node = neighbor_node
            break
        else:
            queue.add(neighbor_node)
```

This code performs the following actions:
- **Checks for unvisited neighbors:** Only neighbors not already visited are processed.
- **Extracts data:** Retrieves the `movie_id` and `person_id` from each neighbor.
- **Creates a Node:** Initializes a new `Node` with the `person_id`, no parent (`None`), and the associated `movie_id`.
- **Target Check:** If the neighbor's `person_id` matches the target, it sets the `target_node` and breaks the loop.
- **Queue Addition:** If the neighbor is not the target, the node is added to the queue for further exploration.

Now after initial neighbour visit we check if the target is already reached because if it is
then there is no need to continue the search and we could just return the found node.

```python
if target_node is not None:
    path = []
    while target_node is not None:
        path.insert(0, (target_node.action, target_node.state))
        target_node = target_node.parent
    print(path)
    return path
```



And now for the most critical part of the algorithm. In this section, we 
process each element from the queue one by one. The steps are as follows:

- **Dequeue and Check:**  
  Remove the next node from the queue and check whether it has already been visited.

- **Target Verification:**  
  If the current node's actor ID matches the target, we save the node as 
  `target_node` and break out of the loop.

- **Neighbor Exploration:**  
  If not, we retrieve all the neighbors of the current actor. For each neighbor, we create a new `Node` object linking the neighbor to the current node, and add it to the queue for future processing.

- **Mark as Visited:**  
  After processing all neighbors, we add the current actor to the `visited` list to ensure it is not processed again.

```python
while not queue.empty():
    current_node = queue.remove()
    current_person_id = current_node.state

    if current_person_id in visited:
        continue

    if current_person_id == target:
        target_node = current_node
        break

    neighbors = neighbors_for_person(current_person_id)

    for neighbor in neighbors:
        neighbor_movie_id = neighbor[0]
        neighbor_person_id = neighbor[1]

        neighbor_node = Node(neighbor_person_id, current_node, neighbor_movie_id)
        queue.add(neighbor_node)

    visited.append(current_person_id)
```

This loop efficiently explores the graph, ensuring each actor is visited only once and 
stopping as soon as the target is found.


And finally, after the loop completes, we assume a connection between the actors 
has been found. In this final phase, we backtrack through the nodes—from the target 
node up to the source—to build a list of connection tuples. Each tuple contains the 
movie ID and actor ID that form a step in the path.

The process is as follows:

- **Backtracking:**  
  Starting from the target node, iterate backwards using each node's parent pointer, and insert a tuple at the beginning of the list. This ensures that the list is in the correct order, starting from the source actor.

- **Return Value:**  
  - If the list is populated (i.e., there is at least one tuple), it is returned as the final path.
  - If the list remains empty, this indicates that no connection was found, and the function returns `None`.

```python
list_to_return = []

while target_node is not None:
    list_to_return.insert(0, (target_node.action, target_node.state))
    target_node = target_node.parent

if len(list_to_return) > 0:
    print(list_to_return)
    return list_to_return

return None
```