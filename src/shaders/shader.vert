#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aOffset;

uniform mat4 uProjection;
uniform vec2 uPlayerPos;
uniform int uIsPlayer;

void main()
{
    vec2 pos = aPos;
    if(uIsPlayer == 0)
        pos += aOffset;
    else
        pos += uPlayerPos;

    gl_Position = uProjection * vec4(pos, 0.0, 1.0);
}