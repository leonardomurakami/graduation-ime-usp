#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

bool compare(ll expected, int left, int right){
    cout << "? " << right - left + 1 << " ";
    for (int i = left; i <= right; i++) { cout << i+1 << " "; }
    cout << endl << flush;
    ll result;
    cin >> result;
    return result == expected;
}

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int t;
    cin >> t;
    for (int i = 0; i < t; i++) {
        int n;
        cin >> n;
        vector<int> arr(n);
        for (int i = 0; i < n; i++) { cin >> arr[i]; }

        vector<ll> prefix(n + 1, 0);
        for (int i = 0; i < n; i++) { prefix[i + 1] = prefix[i] + arr[i]; }

        int left = 0, right = n - 1, mid;
        ll auxsum;

        while (left < right) {
            mid = (left + right) / 2;
            auxsum = prefix[mid+1] - prefix[left];
            if (compare(auxsum, left, mid)) left = mid + 1;
            else right = mid;
        }
        cout << "! " << left + 1 << endl << flush;
    }
    return 0;
}
