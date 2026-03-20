#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int t, n, q;
    cin >> t;
    
    for (int i = 0; i < t; i++) {
        cin >> n >> q;
        vector<int> arr(n);
        for (int j = 0; j < n; j++) { cin >> arr[j]; }
        sort(arr.begin(), arr.end(), greater<int>());
        vector<ll> prefix(n + 1, 0);
        for (int j = 0; j < n; j++) { prefix[j + 1] = prefix[j] + arr[j]; }
        for (int j = 0; j < q; j++) {
            int x;
            cin >> x;
            if (x > prefix[n]) cout << -1 << endl;
            else {
                int low = 1, high = n;
                while (low < high) {
                    int mid = (low + high) / 2;
                    if (prefix[mid] >= x) high = mid;
                    else low = mid + 1;
                }
                cout << low << endl;
            }
        }

    }
    return 0;
}

