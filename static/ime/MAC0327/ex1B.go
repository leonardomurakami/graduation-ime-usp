package main
import "fmt"

func main() {
	var n int
	fmt.Scan(&n)

	if n%2 == 0 && n > 2 {
		fmt.Println("YES")
	} else {
		fmt.Println("NO")
	}
}