#version 330 core

layout (location=0) in vec2 aPos;
layout (location=1) in vec3 vertexColor;

out vec3 fragmentColor;

uniform mat4 uMVP;

void main()
{
    gl_Position = uMVP * vec4(aPos, 0.0, 1.0);
    fragmentColor = vertexColor;
}