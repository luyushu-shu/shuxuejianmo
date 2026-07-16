function result = infection(b,r,m,n,c)
    result = nchoosek(m+n,m);
    for i  = 0:(m-1)
        up = b + i*c;
        down = b + r + i*c;
        result = result * (up/down)
    end
    for j = 0:(n-1)
        up = r + j*c;
        down = b + r + (m+j)*c;
        result = result * (up/down)
    end
end