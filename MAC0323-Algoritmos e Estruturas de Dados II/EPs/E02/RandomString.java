/*
 * $ java-algs4 RandomString 5 8888
 * cbbab
 * $ java-algs4 RandomString 20 8888
 * cbbabebdbcaddbacecbb
 * $ 
 */

import edu.princeton.cs.algs4.StdOut;
import edu.princeton.cs.algs4.StdRandom;

public class RandomString
{

    public static String ran_abcde(int N) {
	StringBuilder s = new StringBuilder();
	String alpha = "abcde";
	for (int i = 0; i < N; i++) {
	    int t = StdRandom.uniformInt(5);
	    s.append(alpha.charAt(t));
	}
	return s.toString();
    }
    
    public static void main(String[] args)
    {
	int N = Integer.parseInt(args[0]);
	long seed = Long.parseLong(args[1]);
	StdRandom.setSeed(seed);
	String s = ran_abcde(N);
	StdOut.println(s);
    }
}
