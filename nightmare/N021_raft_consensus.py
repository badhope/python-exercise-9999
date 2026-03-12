# -----------------------------
# 题目：实现分布式共识算法Raft。
# 描述：支持领导者选举、日志复制、安全性保证。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    index: int
    command: Any

@dataclass
class RequestVoteRequest:
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

@dataclass
class RequestVoteResponse:
    term: int
    vote_granted: bool

@dataclass
class AppendEntriesRequest:
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int

@dataclass
class AppendEntriesResponse:
    term: int
    success: bool

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        self._election_timeout = random.uniform(0.15, 0.3)
        self._heartbeat_interval = 0.05
        self._last_heartbeat = time.time()
        
        self._lock = threading.RLock()
        self._running = False
        self._election_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        
        self._message_queue: Queue = Queue()
        self._votes_received: set = set()
    
    def start(self):
        self._running = True
        self._election_thread = threading.Thread(target=self._election_loop)
        self._election_thread.daemon = True
        self._election_thread.start()
    
    def stop(self):
        self._running = False
    
    def _election_loop(self):
        while self._running:
            time.sleep(0.01)
            
            with self._lock:
                if self.state == NodeState.LEADER:
                    continue
                
                if time.time() - self._last_heartbeat > self._election_timeout:
                    self._start_election()
    
    def _start_election(self):
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self._votes_received = {self.node_id}
        self._last_heartbeat = time.time()
        
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1].term if self.log else 0
        
        request = RequestVoteRequest(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=last_log_index,
            last_log_term=last_log_term
        )
        
        votes = 1
        for peer in self.peers:
            if self._request_vote(peer, request):
                votes += 1
        
        if votes > len(self.peers) / 2:
            self._become_leader()
    
    def _request_vote(self, peer: str, request: RequestVoteRequest) -> bool:
        return random.random() > 0.3
    
    def _become_leader(self):
        with self._lock:
            self.state = NodeState.LEADER
            
            for peer in self.peers:
                self.next_index[peer] = len(self.log)
                self.match_index[peer] = 0
            
            self._start_heartbeat()
    
    def _start_heartbeat(self):
        def heartbeat_loop():
            while self._running and self.state == NodeState.LEADER:
                self._send_heartbeat()
                time.sleep(self._heartbeat_interval)
        
        thread = threading.Thread(target=heartbeat_loop)
        thread.daemon = True
        thread.start()
    
    def _send_heartbeat(self):
        for peer in self.peers:
            request = AppendEntriesRequest(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=len(self.log) - 1,
                prev_log_term=self.log[-1].term if self.log else 0,
                entries=[],
                leader_commit=self.commit_index
            )
            self._append_entries(peer, request)
    
    def _append_entries(self, peer: str, request: AppendEntriesRequest) -> bool:
        return True
    
    def handle_request_vote(self, request: RequestVoteRequest) -> RequestVoteResponse:
        with self._lock:
            if request.term < self.current_term:
                return RequestVoteResponse(self.current_term, False)
            
            if request.term > self.current_term:
                self.current_term = request.term
                self.state = NodeState.FOLLOWER
                self.voted_for = None
            
            if self.voted_for is None or self.voted_for == request.candidate_id:
                self.voted_for = request.candidate_id
                self._last_heartbeat = time.time()
                return RequestVoteResponse(self.current_term, True)
            
            return RequestVoteResponse(self.current_term, False)
    
    def handle_append_entries(self, request: AppendEntriesRequest) -> AppendEntriesResponse:
        with self._lock:
            if request.term < self.current_term:
                return AppendEntriesResponse(self.current_term, False)
            
            self._last_heartbeat = time.time()
            
            if request.term > self.current_term:
                self.current_term = request.term
                self.state = NodeState.FOLLOWER
                self.voted_for = None
            
            return AppendEntriesResponse(self.current_term, True)
    
    def propose(self, command: Any) -> bool:
        with self._lock:
            if self.state != NodeState.LEADER:
                return False
            
            entry = LogEntry(
                term=self.current_term,
                index=len(self.log),
                command=command
            )
            self.log.append(entry)
            return True
    
    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'node_id': self.node_id,
                'state': self.state.value,
                'term': self.current_term,
                'log_length': len(self.log),
                'commit_index': self.commit_index
            }

class RaftCluster:
    def __init__(self, node_ids: List[str]):
        self.nodes: Dict[str, RaftNode] = {}
        
        for node_id in node_ids:
            peers = [n for n in node_ids if n != node_id]
            self.nodes[node_id] = RaftNode(node_id, peers)
    
    def start(self):
        for node in self.nodes.values():
            node.start()
    
    def stop(self):
        for node in self.nodes.values():
            node.stop()
    
    def get_leader(self) -> Optional[str]:
        for node_id, node in self.nodes.items():
            if node.state == NodeState.LEADER:
                return node_id
        return None
    
    def get_cluster_state(self) -> Dict[str, Any]:
        return {
            node_id: node.get_state()
            for node_id, node in self.nodes.items()
        }

def main():
    cluster = RaftCluster(['node1', 'node2', 'node3'])
    cluster.start()
    
    print("等待选举...")
    time.sleep(0.5)
    
    leader = cluster.get_leader()
    print(f"当前领导者: {leader}")
    
    print("\n集群状态:")
    for node_id, state in cluster.get_cluster_state().items():
        print(f"  {node_id}: {state['state']}, term={state['term']}")
    
    cluster.stop()

if __name__ == "__main__":
    main()
