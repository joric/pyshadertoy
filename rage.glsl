void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 q = fragCoord.xy - iResolution.xy * .5;
    int i = int(iTime - atan(q.y, q.x) * 8. / 6.28 + 8.);
    fragColor = vec4(mod(float(i/2),2.), mod(float(i/4),2.), mod(float(i),2.), 1.);
}


/*
// es3 version
void mainImage( out vec4 O, vec2 U )
{
    U  += U - iResolution.xy;
    O = vec4( int(iTime - atan(U.y, U.x) * 8. / 6.28 + 8.) / ivec4(2, 4, 1, 1) % 2 );
}
*/
