#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aOffset;
layout (location = 2) in vec2 aTexCoord;

uniform mat4 uProjection;
uniform vec2 uPlayerPos;
uniform int uIsPlayer;

out vec2 vTexCoord;

void main()
{
    vec2 pos = aPos;
    
    // For instanced rendering (aOffset has divisor=1)
    // For regular rendering (aOffset updated per frame)
    if(uIsPlayer == 0)
        pos += aOffset;
    else
        pos += uPlayerPos;

    vec4 pos4 = vec4(pos, 0.0, 1.0);
    gl_Position = uProjection * pos4;

    vTexCoord = aTexCoord;
} 