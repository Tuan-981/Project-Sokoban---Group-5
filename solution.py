"""Student entry point. See README.md for the API and scoring rules."""
from collections import deque
import time
from sokoban import sokoban_goal_state

def solve(initial_state, timebound=120):
    # hết thời gian ngay từ đầu thì trả False
    if timebound <= 0:
        return False
    deadline = time.time() + timebound
    # trạng thái đầu đã là đích thì trả về chính nó
    if sokoban_goal_state(initial_state) :
        return initial_state
    
    frontier = deque([initial_state])
    visited = {initial_state.hashable_state()}

    while frontier :
        if time.time() >= deadline:
            return False
        # lấy ra khỏi hàng đợi
        current = frontier.popleft()
        # duyệt các trạng thái con
        for child in current.successors():
            key = child.hashable_state()
            if key in visited :
                continue
            #đánh dấu đã thăm
            visited.add(key)
            #là đích thì trả về
            if sokoban_goal_state(child):
                return child
            #chưa phải đích, cho vào CUỐI hàng đợi
            frontier.append(child)
    #hết hàng đợi mà không thấy đích
    return False







