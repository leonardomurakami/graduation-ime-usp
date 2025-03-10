/*
Nome: Leonardo Heidi Almeida Murakami
NUSP: 11260186
*/
import java.util.Random;

public class Jogo {
    private static Random random = new Random();
    private static int MAX_CARD_VALUE = 100;

    public static void main(String[] args) {
        int a = Integer.parseInt(args[0]);
        int b = Integer.parseInt(args[1]);
        int T = Integer.parseInt(args[2]);

        int noChoiceWins = 0;
        int withChoiceWins = 0;

        for (int i = 0; i < T; i++) {
            if (noChoice(a, b)) {
                noChoiceWins++;
            }
            if (withChoice(a, b)) {
                withChoiceWins++;
            }
        }

        double noChoicePercentage = (double) noChoiceWins / T * 100;
        double withChoicePercentage = (double) withChoiceWins / T * 100;

        System.out.printf("No choice: %d - %.2f%%\n", noChoiceWins, noChoicePercentage);
        System.out.printf("With choice: %d - %.2f%%\n", withChoiceWins, withChoicePercentage);
    }
    
    public static boolean noChoice(int a, int b) {
        int choice = random.nextInt(2);
        return (choice == 0) ? (a > b) : (b > a);
    }
    
    public static boolean withChoice(int a, int b) {
        int knownCard = random.nextInt(2);
        int knownValue = (knownCard == 0) ? a : b;
        int unknownValue = (knownCard == 0) ? b : a;
        
        double stickProbability = (double) knownValue / MAX_CARD_VALUE;
    
        if (random.nextDouble() < stickProbability) {
            return knownValue > unknownValue;
        } else {
            return unknownValue > knownValue;
        }
    }
}
