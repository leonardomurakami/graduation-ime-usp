import java.util.ArrayList;
import java.util.Random;

public class FugaGato {
    private static final int ANIMATION_DELAY = 10;

    private final int gridSize;
    private boolean[][] visited;
    private int catX, catY;
    private ArrayList<int[]> path;
    private final Random random;

    public FugaGato(int gridSize) {
        this.gridSize = gridSize;
        this.random = new Random();
        resetSimulation();
        initializeGraphics();
    }

    private void initializeGraphics() {
        StdDraw.setXscale(0, gridSize);
        StdDraw.setYscale(0, gridSize);
        StdDraw.enableDoubleBuffering();
    }

    public void resetSimulation() {
        visited = new boolean[gridSize][gridSize];
        catX = gridSize / 2;
        catY = gridSize / 2;
        path = new ArrayList<>();
        path.add(new int[]{catX, catY});
        visited[catY][catX] = true;
    }

    private void draw() {
        StdDraw.clear();

        // desenhar grid
        StdDraw.setPenColor(StdDraw.LIGHT_GRAY);
        for (int i = 0; i <= gridSize; i++) {
            StdDraw.line(i, 0, i, gridSize);
            StdDraw.line(0, i, gridSize, i);
        }

        // desenhar caminho do gato
        StdDraw.setPenColor(StdDraw.BLUE);
        for (int i = 1; i < path.size(); i++) {
            int[] p1 = path.get(i - 1);
            int[] p2 = path.get(i);
            StdDraw.line(p1[0], p1[1], p2[0], p2[1]);
        }

        StdDraw.show();
    }

    public int runSimulation() {
        resetSimulation();
        int steps = 0;

        while (!isEscaped()) {
            draw();
            StdDraw.pause(ANIMATION_DELAY);

            int[][] directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
            ArrayList<int[]> possibleMoves = new ArrayList<>();

            for (int[] dir : directions) {
                int newX = catX + dir[0];
                int newY = catY + dir[1];
                if (isValidMove(newX, newY)) {
                    possibleMoves.add(new int[]{newX, newY});
                }
            }

            if (possibleMoves.isEmpty()) {
                break;  // gato sem movimentos possíveis
            }

            int[] move = possibleMoves.get(random.nextInt(possibleMoves.size()));
            catX = move[0];
            catY = move[1];
            visited[catY][catX] = true;
            path.add(new int[]{catX, catY});
            steps++;
        }

        return steps;
    }

    private boolean isEscaped() {
        return catX == 0 || catX == gridSize - 1 || catY == 0 || catY == gridSize - 1;
    }

    private boolean isValidMove(int x, int y) {
        return x >= 0 && x < gridSize && y >= 0 && y < gridSize && !visited[y][x];
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            StdOut.println("Usage: java FugaGato <grid_size> <number_of_simulations>");
            return;
        }

        int gridSize = Integer.parseInt(args[0]);
        int numSimulations = Integer.parseInt(args[1]);

        FugaGato fugaGato = new FugaGato(gridSize);

        StdOut.println("---------------------------------------");
        StdOut.println(" Simulação  ---  quantidade de passos  ");
        StdOut.println("---------------------------------------");

        int trappedCount = 0;
        for (int i = 0; i < numSimulations; i++) {
            int steps = fugaGato.runSimulation();
            StdOut.printf("      %d     ---           %3d  %n", i, steps);
            if (steps > 0 && !fugaGato.isEscaped()) {
                trappedCount++;
            }
            StdDraw.pause(ANIMATION_DELAY);  // pequena pausa entre simulações
        }

        StdOut.println("---------------------------------------");
        double trappedPercentage = (double) trappedCount / numSimulations * 100;
        StdOut.printf("O gato ficou sem saída %.0f%% das vezes%n", trappedPercentage);
        StdOut.println("---------------------------------------");

        StdDraw.pause(1000);
        System.exit(0);
    }
}