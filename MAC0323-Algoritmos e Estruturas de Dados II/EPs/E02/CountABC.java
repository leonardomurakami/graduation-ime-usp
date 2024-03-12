import java.math.BigInteger;

import edu.princeton.cs.algs4.StdIn;
import edu.princeton.cs.algs4.StdOut;
import edu.princeton.cs.algs4.Stopwatch;

public class CountABC
{
    public static long countABC(String s) {
		int N = s.length();
		long aCount = 0, abCount = 0, abcCount = 0;

		for (int i = 0; i < N; i++) {
			char c = s.charAt(i);
			if (c == 'a') {
				aCount++; // Contamos todas as ocorrências de 'a'
			} else if (c == 'b') {
				abCount += aCount; // Para cada 'b', adicionamos o número de 'a' antes dele
			} else if (c == 'c') {
				abcCount += abCount; // Para cada 'c', adicionamos o número de "ab" formados antes dele
			}
		}
		return abcCount;
    }

// BigInteger variant for testing big numbers
//	public static BigInteger bigCountABC(String s) {
//		int N = s.length();
//		BigInteger aCount = new BigInteger("0"), abCount = new BigInteger("0"), abcCount = new BigInteger("0");
//		for (int i = 0; i < N; i++) {
//			char c = s.charAt(i);
//			if (c == 'a') {
//				aCount = aCount.add(BigInteger("1")); // Contamos todas as ocorrências de 'a'
//			} else if (c == 'b') {
//				abCount = abCount.add(aCount); // Para cada 'b', adicionamos o número de 'a' antes dele
//			} else if (c == 'c') {
//				abcCount = abcCount.add(abCount); // Para cada 'c', adicionamos o número de "ab" formados antes dele
//			}
//		}
//		return abcCount;
//	}

    public static long countABCPlain(String s) {
	int N = s.length();
	long t = 0;
	for (int i = 0; i < N; i++) 
	    for (int j = i + 1; j < N; j++) 
		for (int k = j + 1; k < N; k++)  
		    if (s.charAt(i) == 'a' && s.charAt(j) == 'b' && s.charAt(k) == 'c')
			t++;
	return t;
    }    
    
    public static void main(String[] args)
    {
	String s = StdIn.readString();
	Stopwatch sw = new Stopwatch();
	StdOut.println(countABC(s));
	StdOut.println("time: " + sw.elapsedTime());
	sw = new Stopwatch();
	StdOut.println(countABCPlain(s));
	StdOut.println("time: " + sw.elapsedTime());
    }
}
