#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int n, t;
    cin >> n >> t;
    vector<int> arr(n);
    for (int i = 0; i < n; i++) { cin >> arr[i]; }
    
    int left = 0, right = 0, max_length = 0;
    ll current_sum = 0;

    while (right < n) {
        current_sum += arr[right];
        while (current_sum > t) { current_sum -= arr[left]; left++; }
        max_length = max(max_length, right - left + 1);
        right++;
    }
    cout << max_length << endl;
    return 0;
}
