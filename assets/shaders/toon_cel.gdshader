shader_type spatial;
render_mode diffuse_toon, specular_toon, cull_back;

uniform vec4 base_color : source_color = vec4(0.8, 0.8, 0.8, 1.0);
uniform vec4 shadow_tint : source_color = vec4(0.55, 0.55, 0.65, 1.0);
uniform float shadow_threshold : hint_range(0.0, 1.0) = 0.45;
uniform float shadow_smoothness : hint_range(0.0, 0.2) = 0.05;

void fragment() {
    ALBEDO = base_color.rgb;
    ROUGHNESS = 0.9;
    METALLIC = 0.0;
}

void light() {
    float n_dot_l = dot(NORMAL, LIGHT);
    float light_intensity = smoothstep(shadow_threshold - shadow_smoothness, shadow_threshold + shadow_smoothness, n_dot_l);
    vec3 mixed_color = mix(shadow_tint.rgb * ALBEDO, ALBEDO, light_intensity);
    DIFFUSE_LIGHT += mixed_color * LIGHT_COLOR * ATTENUATION;
}
