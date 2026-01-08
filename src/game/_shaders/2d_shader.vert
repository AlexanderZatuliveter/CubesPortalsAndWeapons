#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aOffset;
layout (location = 2) in vec2 aTexCoord;

uniform mat4 uProjection;
uniform mat4 rotation;
uniform bool uApplyRotation;
uniform vec2 uPlayerPos;
uniform int uIsPlayer;

out vec2 vTexCoord;

void main()
{
    vec2 pos = aPos;
    if(uIsPlayer == 0)
        pos += aOffset;
    else
        pos += uPlayerPos;

    vec4 pos4 = vec4(pos, 0.0, 1.0);
    if (uApplyRotation)
        gl_Position = uProjection * rotation * pos4;
    else
        gl_Position = uProjection * pos4;

    vTexCoord = aTexCoord;
} 