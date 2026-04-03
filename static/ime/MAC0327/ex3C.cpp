#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long
#define MODULO 1000000007
#define MAXN 1000005

int dp[MAXN][2];

void precompute() {
    dp[1][0] = 1;
    dp[1][1] = 1;
    
    for (int i = 2; i < MAXN; ++i) {
        dp[i][0] = (4LL * dp[i - 1][0] + dp[i - 1][1]) % MODULO;
        dp[i][1] = (dp[i - 1][0] + 2LL * dp[i - 1][1]) % MODULO;
    }
}

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    
    precompute();

    int t;
    cin >> t;

    for (int i = 0; i < t; i++) {
        int n;
        cin >> n;
        
        cout << (dp[n][0] + dp[n][1]) % MODULO << endl;
    }
}
