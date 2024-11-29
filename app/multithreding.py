# # from fastapi import FastAPI
# # from concurrent.futures import ThreadPoolExecutor
# # from typing import List
# # import time

# # app = FastAPI()

# # # Create a ThreadPoolExecutor to manage threads
# # executor = ThreadPoolExecutor(max_workers=10)

# # # Example list of 50 numbers
# # numbers = [i for i in range(1, 51)]  # A list of numbers from 1 to 50

# # def process_chunk(chunk: List[int]):
# #     """Simulate a blocking task that processes a chunk of numbers."""
# #     time.sleep(2)  # Simulate some processing time (e.g., 2 seconds)
# #     print(f"Processed chunk: {chunk}")
# #     return chunk

# # def split_list(lst: List[int], chunk_size: int) -> List[List[int]]:
# #     """Splits the input list into smaller chunks of a given size."""
# #     return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# # @app.get("/process_numbers/")
# # async def process_numbers():
# #     """Process the list of numbers in chunks of 5 using multithreading."""
    
# #     # Split the list into chunks of 5 numbers each
# #     chunks = split_list(numbers, 5)

# #     # Run each chunk in a separate thread using the ThreadPoolExecutor
# #     futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
    
# #     # Wait for all threads to complete and collect the results
# #     results = [future.result() for future in futures]
    
# #     return {"message": "Processing complete", "processed_chunks": results}




# from fastapi import FastAPI
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import List
# import time

# app = FastAPI()

# # Create a ThreadPoolExecutor with a maximum of 5 workers (threads)
# executor = ThreadPoolExecutor(max_workers=5)

# # Example list of 50 numbers
# numbers = [i for i in range(1, 51)]  # A list of numbers from 1 to 50

# def process_chunk(chunk: List[int]):
#     """Simulate a blocking task that processes a chunk of numbers."""
#     time.sleep(2)
#     # Simulate some processing time (e.g., 2 seconds)
#     print(f"Processed chunk: {chunk}")
#     for ele in chunk:
#         time.sleep(2) 
#         print(ele)
#     return chunk

# def split_list(lst: List[int], chunk_size: int) -> List[List[int]]:
#     """Splits the input list into smaller chunks of a given size."""
#     return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# @app.get("/process_numbers/")
# async def process_numbers():
#     """Process the list of numbers in chunks of 5 using multithreading (5 threads at a time)."""
    
#     # Split the list into chunks of 5 numbers each
#     chunks = split_list(numbers, 5)

#     # Run each chunk in a separate thread (5 threads at a time)
#     futures = []
#     results = []
    
#     # Process chunks in batches of 5 (using ThreadPoolExecutor with max_workers=5)
#     for i in range(0, len(chunks), 5):
#         # Submit tasks for the next 5 chunks (or fewer if there are less than 5 remaining)
#         batch_chunks = chunks[i:i+5]
#         for chunk in batch_chunks:
#             futures.append(executor.submit(process_chunk, chunk))

#         # Wait for each of the futures to complete and collect the results
#         for future in as_completed(futures):
#             results.append(future.result())
        
#         # Clear the futures list after processing the current batch
#         futures.clear()

#     return {"message": "Processing complete", "processed_chunks": results}


from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import time

app = FastAPI()

# Create a ThreadPoolExecutor with a maximum of 5 workers (threads)
executor = ThreadPoolExecutor(max_workers=5)

# Example list of 50 numbers
numbers = [i for i in range(1, 51)]  # A list of numbers from 1 to 50

def process_chunk(chunk: List[int], chunk_id: int):
    """Simulate a blocking task that processes a chunk of numbers."""
    # Simulating different processing times for each chunk
    time.sleep(chunk_id % 3 + 1)  # Varying sleep times to simulate different processing times
    print(f"Processed chunk {chunk_id}: {chunk}")
    for ele in chunk:
        print(ele)
    return chunk_id, chunk  # Return chunk id and the chunk itself for identification

def split_list(lst: List[int], chunk_size: int) -> List[List[int]]:
    """Splits the input list into smaller chunks of a given size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

@app.get("/process_numbers/")
async def process_numbers():
    """Process the list of numbers in chunks of 5 using multithreading (5 threads at a time)."""
    
    # Split the list into chunks of 5 numbers each
    chunks = split_list(numbers, 5)

    # Run each chunk in a separate thread (5 threads at a time)
    futures = []
    results = []
    
    # Process chunks in batches of 5 (using ThreadPoolExecutor with max_workers=5)
    for i in range(0, len(chunks), 5):
        # Submit tasks for the next 5 chunks (or fewer if there are less than 5 remaining)
        batch_chunks = chunks[i:i+5]
        for chunk_id, chunk in enumerate(batch_chunks, start=i):
            futures.append(executor.submit(process_chunk, chunk, chunk_id))

        # Wait for each of the futures to complete and collect the results
        for future in as_completed(futures):
            chunk_id, chunk = future.result()
            results.append((chunk_id, chunk))
        
        # Clear the futures list after processing the current batch
        futures.clear()

    return {"message": "Processing complete", "processed_chunks": results}


