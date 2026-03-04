package main
import "fmt"

func main() {
	var n int
	fmt.Scan(&n)

	for i := 1; i <= n; i++ {
		var m int
		fmt.Scan(&m)
		
		var s string
		fmt.Scan(&s)
		
		max_alphabet := 1
		for j := 0; j < m; j++ {
			max_alphabet = max(max_alphabet, int(s[j]-'a')+1)
		}

		fmt.Println(max_alphabet)
	}
}