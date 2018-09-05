void mainImage( out vec4 O, vec2 U )
{
    U  += U - iResolution.xy;
    O = vec4( int(iTime - atan(U.y, U.x) * 8. / 6.28 + 8.) / ivec4(2, 4, 1, 1) % 2 );
}
