function prob = sampling_with_replacement(b,r,m,n)
    prob = nchoosek(m+n,m) * (b^m*r^n)/(b + r) ^ (m + n)
end