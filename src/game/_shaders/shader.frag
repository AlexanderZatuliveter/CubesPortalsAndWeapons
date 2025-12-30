#version 330 core

uniform vec4 uColor;
uniform int uUseTexture;
uniform sampler2D uTexture;

in vec2 vTexCoord;
out vec4 FragColor;

void main()
{
    if(uUseTexture == 1)
    {
        vec4 tex = texture(uTexture, vTexCoord);
        // Multiply sampled color by uniform color to allow tinting
        FragColor = tex * uColor;
    }
    else
    {
        FragColor = uColor;
    }
}