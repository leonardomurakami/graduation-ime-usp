#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long
#define MODULO 1000000007

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int n;
    cin >> n;

    vector<string> grid(n);
    for (int i = 0; i < n; i++) cin >> grid[i];

    vector<vector<ll>> dp(n, vector<ll>(n, 0));

    dp[0][0] = (grid[0][0] == '.') ? 1 : 0;

    for (int i = 1; i < n; i++) { dp[0][i] = (grid[0][i] == '.') ? dp[0][i-1] : 0; }

    for (int i = 1; i < n; i++) { dp[i][0] = (grid[i][0] == '.') ? dp[i-1][0] : 0; }

    for (int i = 1; i < n; i++) {
        for (int j = 1; j < n; j++){
            dp[i][j] = (grid[i][j] == '.') ? (dp[i-1][j] + dp[i][j-1]) % MODULO : 0;
        }
    }

    cout << dp[n-1][n-1] << endl;
}
