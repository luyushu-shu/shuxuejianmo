function prob = sampling_without_replacement(b,r,m,n)
    if m >= b || n >= r
        error("Be Sure b > m and r > n")
    end
    prob = nchoosek(b,m)*nchoosek(r,n)/nchoosek(b+r,m+n);
end