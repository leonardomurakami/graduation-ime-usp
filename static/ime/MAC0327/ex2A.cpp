#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

bool split(ll mid, const vector<int>& arr, int k){
    int count = 1;
    ll current_sum = 0;
    for (int i = 0; i < arr.size(); i++){
        if (arr[i] + current_sum <= mid) current_sum += arr[i];
        else {
            count++; 
            current_sum = arr[i];
            if (count > k) return false;
        } 
    }
    return true;
}

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int n, k;
    cin >> n >> k;
    vector<int> arr(n);
    for (int i = 0; i < n; i++) { cin >> arr[i]; }
    ll low = *max_element(arr.begin(), arr.end());
    ll high = accumulate(arr.begin(), arr.end(), 0LL);
    while (low < high) {
        ll mid = (low + high) / 2;
        if (split(mid, arr, k)) high = mid;
        else low = mid + 1;
    }
    cout << low << endl;
    return 0;
}