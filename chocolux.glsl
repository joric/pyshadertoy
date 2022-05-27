#ifdef GL_ES
precision highp float;
#endif

uniform float time;

void main(void)
{
    vec3 s[4];
    s[0]=vec3(0);
    s[3]=vec3(sin(time),cos(time),0);
    s[1]=s[3].zxy;
    s[2]=s[3].zzx;

    float t,b,c,h=0.0;
    vec3 m,n;
    vec3 p=vec3(.2);
    vec3 d=normalize(.001*gl_FragCoord.rgb-p);
    for(int i=0;i<4;i++)
    {
        t=2.0;
        for(int i=0;i<4;i++)
        {
            b=dot(d,n=s[i]-p);
            c=b*b+.2-dot(n,n);
            if(b-c<t)
            if(c>0.0)
            {
                m=s[i];t=b-c;
            }
        }
    p+=t*d;
    d=reflect(d,n=normalize(p-m));
    h+=pow(n.x*n.x,44.)+n.x*n.x*.2;
    }
    gl_FragColor=vec4(h,h*h,h*h*h*h,1);
}
