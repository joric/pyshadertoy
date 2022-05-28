void mainImage(out vec4 c, vec2 p)
{
  p = p*2./iResolution.xy-1.;
  vec3 b = vec3(30.*iTime, 15, 4);
 
  for (float w = 99., d = 1., s = p.y; b.z < w; c = d*b.zzzz/99.-s)
  {
    ivec3 e = ivec3(b += vec3(p.xy, 1));
    if (e.y < (32<e.z && 27<e.x%99 ? (e.x/9^e.z/8)*8%46 : 0))
      s = float((-e.y&e.x&e.z)%3)/b.z,
      d < (p.x = p.y = 1.) ? w = d : d = b.z/w;
  }
}
