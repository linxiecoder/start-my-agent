你是一个软件工程师，可以生成代码。

问：帮我实现图的深度优先搜索算法。
答：我用Java语言来通过递归和遍历实现
时间复杂度分析
假设：
V = 顶点数
E = 边数
在邻接表表示的图中：
1.访问每个顶点一次 → O(V)
2.遍历每条边一次（无向图中每条边会在两个顶点的邻接表中出现一次） → O(E)
因此，DFS 的总时间复杂度为： 
T(V,E)=O(V+E)
空间复杂度分析
visited 数组：O(V)
递归调用栈：最坏情况下（图为链状），递归深度为 
O(V)
邻接表存储：
O(V+E)
总空间复杂度： 
S(V,E)=O(V+E)
✅ 总结：
时间复杂度：
O(V+E)
空间复杂度：
O(V+E)（包含存储和递归栈）
邻接表实现 DFS 在稀疏图和稠密图中都表现良好，递归实现简单但在V很大时可能会栈溢出，可改为显式栈的迭代版本。
（一）递归实现
以下是使用递归实现 DFS 的 Java 代码示例，代码中添加了详细注释以便理解：
```java
import java.util.*;
 
public class DFSRecursive {
    private boolean[] visited; // 用于标记节点是否访问过
    private List<List<Integer>> graph; // 存储图的邻接表
 
    // 构造函数，初始化图的节点数和邻接表
    public DFSRecursive(int n) {
        visited = new boolean[n];
        graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
    }
 
    // 添加边的方法，用于构建图
    public void addEdge(int u, int v) {
        graph.get(u).add(v);
    }
 
    // DFS 的递归实现
    public void dfs(int node) {
        visited[node] = true; // 标记当前节点为已访问
        System.out.print(node + " "); // 打印当前节点
        // 遍历当前节点的所有邻接节点
        for (int neighbor : graph.get(node)) {
            if (!visited[neighbor]) { // 如果邻接节点未访问过
                dfs(neighbor); // 递归调用 DFS
            }
        }
    }
 
    // DFS 遍历的入口方法
    public void dfsTraversal(int start) {
        Arrays.fill(visited, false); // 初始化访问标记数组
        dfs(start); // 从起始节点开始进行 DFS
    }
 
    public static void main(String[] args) {
        DFSRecursive dfs = new DFSRecursive(6); // 创建一个包含 6 个节点的图
        dfs.addEdge(0, 1); // 添加边
        dfs.addEdge(0, 2);
        dfs.addEdge(1, 3);
        dfs.addEdge(2, 4);
        dfs.addEdge(3, 5);
        dfs.addEdge(4, 5);
 
        System.out.println("DFS Traversal:");
        dfs.dfsTraversal(0); // 从节点 0 开始进行 DFS 遍历
    }
}
```
（二）迭代实现
以下是使用迭代实现 DFS 的 Java 代码示例，代码中添加了详细注释以便理解：
```java
import java.util.*;
 
public class DFSIterative {
    private boolean[] visited; // 用于标记节点是否访问过
    private List<List<Integer>> graph; // 存储图的邻接表
 
    // 构造函数，初始化图的节点数和邻接表
    public DFSIterative(int n) {
        visited = new boolean[n];
        graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
    }
 
    // 添加边的方法，用于构建图
    public void addEdge(int u, int v) {
        graph.get(u).add(v);
    }
 
    // DFS 的迭代实现
    public void dfsTraversal(int start) {
        Stack<Integer> stack = new Stack<>(); // 使用栈来模拟递归
        stack.push(start); // 将起始节点压入栈
        visited[start] = true; // 标记起始节点为已访问
 
        while (!stack.isEmpty()) { // 当栈不为空时
            int node = stack.pop(); // 弹出栈顶节点
            System.out.print(node + " "); // 打印当前节点
            // 遍历当前节点的所有邻接节点
            for (int neighbor : graph.get(node)) {
                if (!visited[neighbor]) { // 如果邻接节点未访问过
                    stack.push(neighbor); // 将邻接节点压入栈
                    visited[neighbor] = true; // 标记为已访问
                }
            }
        }
    }
 
    public static void main(String[] args) {
        DFSIterative dfs = new DFSIterative(6); // 创建一个包含 6 个节点的图
        dfs.addEdge(0, 1); // 添加边
        dfs.addEdge(0, 2);
        dfs.addEdge(1, 3);
        dfs.addEdge(2, 4);
        dfs.addEdge(3, 5);
        dfs.addEdge(4, 5);
 
        System.out.println("DFS Traversal:");
        dfs.dfsTraversal(0); // 从节点 0 开始进行 DFS 遍历
    }
}
```
