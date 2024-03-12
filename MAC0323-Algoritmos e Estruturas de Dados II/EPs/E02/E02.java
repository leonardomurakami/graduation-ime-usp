import edu.princeton.cs.algs4.StdIn;
import edu.princeton.cs.algs4.StdOut;
import edu.princeton.cs.algs4.StdRandom;
import edu.princeton.cs.algs4.Stopwatch;

public class E02
{
    public static void main(String[] args)
    {
	int N = Integer.parseInt(args[0]);
	long seed = Long.parseLong(args[1]);
	
	StdRandom.setSeed(seed);
	StdOut.println("Fast counting:");
	for (int n = 8; n <= N; n *= 2) {
	    String s = RandomString.ran_abcde(n);
	    Stopwatch sw = new Stopwatch();
	    StdOut.print(n + ": " + CountABC.countABC(s));
	    StdOut.println(" [time: " + sw.elapsedTime() + "]");
	}

	StdRandom.setSeed(seed);
	StdOut.println("Plain counting:");
	for (int n = 8; n <= N; n *= 2) {
	    String s = RandomString.ran_abcde(n);
	    Stopwatch sw = new Stopwatch();
	    StdOut.print(n + ": " + CountABC.countABCPlain(s));
	    StdOut.println(" [time: " + sw.elapsedTime() + "]");
	}
	
    }

}
