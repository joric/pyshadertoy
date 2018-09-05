void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 q = fragCoord.xy - iResolution.xy * .5;
    int i = int(iTime - atan(q.y, q.x) * 8. / 6.28 + 8.);
    fragColor = vec4(mod(float(i/2),2.), mod(float(i/4),2.), mod(float(i),2.), 1.);
}
